package uts.sdk.modules.mytoolsClicker

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.app.KeyguardManager
import android.content.Context
import android.content.res.ColorStateList
import android.graphics.Canvas
import android.graphics.ColorFilter
import android.graphics.Paint
import android.graphics.Path
import android.graphics.PixelFormat
import android.graphics.Point
import android.graphics.drawable.Drawable
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.RippleDrawable
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.text.InputType
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewConfiguration
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import android.widget.ScrollView
import android.widget.TextView
import org.json.JSONArray
import java.util.UUID
import org.json.JSONObject

class ClickerService : AccessibilityService() {
    companion object {
        @Volatile private var activeService: ClickerService? = null

        @JvmStatic fun isReady(): Boolean = activeService != null

        private val changes = linkedMapOf<String, JSONObject>()

        @JvmStatic fun configure(json: String, id: String, edit: Boolean): Boolean {
            val service = activeService ?: return false
            val plans = runCatching {
                val source = JSONArray(json)
                (0 until source.length()).mapNotNull { index ->
                    runCatching { Plan.fromJson(source.getJSONObject(index)) }.getOrNull()
                }
            }.getOrNull() ?: return false
            val selected = plans.firstOrNull { it.id == id } ?: return false
            service.handler.post {
                if (activeService === service) {
                    service.plans.clear()
                    plans.forEach { service.plans[it.id] = it }
                    service.selected = selected
                    service.editing = edit
                    service.collapsed = false
                    service.choosing = false
                    service.editingStep = null
                    service.showPanel()
                }
            }
            return true
        }

        @JvmStatic fun drainChanges(): String = synchronized(changes) {
            if (activeService == null) return@synchronized "[]"
            val json = JSONArray(changes.values.toList()).toString()
            changes.clear()
            activeService?.persistChanges()
            json
        }
    }

    private data class Position(var x: Float, var y: Float)

    private enum class ToolIcon { SHOW, HIDE, PLANS, EDIT, TAP, SWIPE }

    private data class Step(
        var swipe: Boolean, val start: Position, val end: Position, var duration: Long? = null
    )

    private data class Plan(
        val id: String, val name: String, val interval: Long,
        val count: Int, val duration: Long, val steps: MutableList<Step>, val data: JSONObject
    ) {
        companion object {
            fun fromJson(data: JSONObject): Plan {
                val action = data.getString("action")
                require(action == "tap" || action == "swipe")
                fun point(item: JSONObject, x: String, y: String, defaultY: Double): Position {
                    val px = item.optDouble(x, 50.0)
                    val py = item.optDouble(y, defaultY)
                    require(px in 0.0..100.0 && py in 0.0..100.0)
                    return Position(px.toFloat() / 100f, py.toFloat() / 100f)
                }
                fun step(item: JSONObject) = Step(item.optString("action", action) == "swipe",
                    point(item, "x", "y", 65.0), point(item, "endX", "endY", 35.0),
                    item.optLong("duration").takeIf { it in 1L..10000L })
                val values = data.optJSONArray("points")
                val steps = if (values != null && values.length() > 0) {
                    require(values.length() <= 20)
                    (0 until values.length()).map { step(values.getJSONObject(it)) }.toMutableList()
                } else mutableListOf(step(data))
                val interval = data.getLong("interval")
                val count = data.getInt("count")
                val duration = data.optLong("swipeDuration", 300L).coerceIn(1L, 10000L)
                require(interval in 1L..60000L && count in 1..10000 && duration in 1L..10000L)
                return Plan(data.getString("id"), data.getString("name"),
                    interval, count, duration, steps, data)
            }
        }

        fun snapshot(): JSONObject {
            val points = JSONArray()
            steps.forEach { step ->
                val point = JSONObject().put("action", if (step.swipe) "swipe" else "tap")
                    .put("x", step.start.x * 100.0).put("y", step.start.y * 100.0)
                    .put("endX", step.end.x * 100.0).put("endY", step.end.y * 100.0)
                step.duration?.let { point.put("duration", it) }
                points.put(point)
            }
            return JSONObject(data.toString()).put("points", points)
        }
    }

    private val handler = Handler(Looper.getMainLooper())
    private val windows by lazy { getSystemService(Context.WINDOW_SERVICE) as WindowManager }
    private var panel: LinearLayout? = null
    private var startButton: Button? = null
    private var generation = 0
    private var inFlight = false
    private val plans = linkedMapOf<String, Plan>()
    private var selected: Plan? = null
    private var editing = false
    private var collapsed = false
    private var choosing = false
    private var editingStep: Int? = null
    private val markers = mutableListOf<Button>()

    override fun onServiceConnected() {
        super.onServiceConnected()
        synchronized(changes) {
            val saved = getSharedPreferences("clicker_pending", Context.MODE_PRIVATE)
                .getString("plans", "[]") ?: "[]"
            runCatching {
                val items = JSONArray(saved)
                for (i in 0 until items.length()) {
                    val item = items.getJSONObject(i)
                    changes.putIfAbsent(item.getString("id"), item)
                }
            }
        }
        activeService = this
    }

    private fun persistChanges() {
        val saved = JSONArray(changes.values.filter { it.optString("id") != "__draft__" })
        getSharedPreferences("clicker_pending", Context.MODE_PRIVATE)
            .edit().putString("plans", saved.toString()).apply()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
    override fun onInterrupt() = stop()

    override fun onDestroy() {
        if (activeService === this) activeService = null
        closeControls()
        super.onDestroy()
    }

    private fun showPanel() {
        val plan = selected ?: return
        closeControls()
        val toolSize = dp(((resources.configuration.screenWidthDp - 36) / 6).coerceIn(32, 48))
        val controls = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(4), dp(4), dp(4), dp(4))
            background = roundedBackground(0x90112440.toInt(), 16, 0x5078dcff)
        }
        val toolbar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        controls.addView(toolbar)
        fun tool(
            symbol: String,
            label: String,
            tint: Int = 0xffeef8ff.toInt(),
            icon: ToolIcon? = null,
            action: () -> Unit,
        ): Button {
            val button = overlayButton(symbol, label, tint, 22f).apply {
                if (icon != null) foreground = drawToolIcon(icon, tint)
                setOnClickListener { action() }
            }
            val layout = LinearLayout.LayoutParams(toolSize, dp(46)).apply {
                setMargins(dp(1), 0, dp(1), 0)
            }
            toolbar.addView(button, layout)
            return button
        }
        fun caption(text: String) = TextView(this).apply {
            this.text = text
            setTextColor(0xffeef8ff.toInt())
            textSize = 13f
            setPadding(dp(8), dp(6), dp(8), dp(4))
        }.also { controls.addView(it) }

        val stepIndex = editingStep
        val currentStep = stepIndex?.let { plan.steps.getOrNull(it) }
        val acceptsKeyboard = !collapsed && currentStep != null
        if (collapsed) {
            tool("", "显示连点器", icon = ToolIcon.SHOW) { collapsed = false; showPanel() }
        } else if (stepIndex != null && currentStep != null) {
            val action = if (currentStep.swipe) "滑动" else "点击"
            val otherAction = if (currentStep.swipe) "点击" else "滑动"
            val timeLabel = if (currentStep.swipe) "滑动时长" else "点击时间"
            controls.removeView(toolbar)
            caption("标记 ${stepIndex + 1} · $action")
            val label = caption("$timeLabel（毫秒）")
            val input = EditText(this).apply {
                id = View.generateViewId()
                inputType = InputType.TYPE_CLASS_NUMBER
                setSingleLine(true)
                imeOptions = EditorInfo.IME_ACTION_DONE
                gravity = Gravity.CENTER_VERTICAL or Gravity.START
                setSelectAllOnFocus(true)
                setText(durationOf(plan, currentStep).toString())
                setTextColor(0xffeef8ff.toInt())
                textSize = 18f
                setPadding(dp(10), 0, dp(10), 0)
                background = roundedBackground(0x993b6b99.toInt(), 10, 0x5078dcff)
            }
            label.labelFor = input.id
            controls.addView(input, LinearLayout.LayoutParams(dp(184), dp(44)).apply {
                setMargins(dp(4), 0, dp(4), dp(4))
            })
            controls.addView(toolbar)
            controls.isFocusableInTouchMode = true
            controls.requestFocus()

            fun applyTime() {
                val duration = input.text.toString().toLongOrNull()
                if (duration == null || duration !in 1L..10000L) {
                    input.error = "请输入 1 至 10000 毫秒"
                    input.requestFocus()
                    return
                }
                currentStep.duration = duration
                getSystemService(InputMethodManager::class.java)?.hideSoftInputFromWindow(input.windowToken, 0)
                editingStep = null
                showPanel()
            }
            input.setOnEditorActionListener { _, actionId, _ ->
                if (actionId != EditorInfo.IME_ACTION_DONE) return@setOnEditorActionListener false
                applyTime()
                true
            }
            tool("⇄", "切换为$otherAction") {
                currentStep.swipe = !currentStep.swipe
                currentStep.duration = null
                showPanel()
            }
            tool("✓", "完成设置", 0xffa5efd6.toInt()) { applyTime() }
        } else if (choosing) {
            tool("‹", "返回") { choosing = false; showPanel() }
            val list = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
            fun planButton(parent: LinearLayout, label: String, tint: Int = 0xffeef8ff.toInt(), action: () -> Unit) {
                val button = overlayButton(label, label, tint, 14f).apply {
                    gravity = Gravity.CENTER_VERTICAL or Gravity.START
                    setPadding(dp(12), 0, dp(12), 0)
                    setOnClickListener { action() }
                }
                parent.addView(button, LinearLayout.LayoutParams(-1, dp(44)).apply {
                    topMargin = dp(4)
                })
            }
            val chooser = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
            controls.addView(chooser, LinearLayout.LayoutParams(dp(216), -2))
            planButton(chooser, "✓  ${plan.name}", 0xffa5efd6.toInt()) {
                choosing = false
                showPanel()
            }
            val otherPlans = plans.values.filter { it.id != "__draft__" && it.id != plan.id }
            otherPlans.forEach { item ->
                planButton(list, item.name) {
                    selected = item
                    choosing = false
                    editing = !item.data.has("points")
                    showPanel()
                }
            }
            if (otherPlans.isNotEmpty()) {
                val availableHeight = (resources.configuration.screenHeightDp - 174).coerceAtLeast(48)
                val listHeight = minOf(otherPlans.size.coerceAtMost(4) * 48, availableHeight)
                chooser.addView(ScrollView(this).apply { addView(list) },
                    LinearLayout.LayoutParams(-1, dp(listHeight)))
            }
            planButton(chooser, "+  新建方案") { createPlan() }
        } else if (editing) {
            fun addStep(swipe: Boolean) {
                if (plan.steps.size >= 20) {
                    toast("最多添加 20 组标记")
                } else {
                    val y = (0.56f + (plan.steps.size % 8) * 0.045f).coerceAtMost(0.90f)
                    plan.steps.add(Step(swipe, Position(0.35f, y), Position(0.66f, y - 0.20f)))
                    showPanel()
                }
            }
            tool("", "添加点击", icon = ToolIcon.TAP) { addStep(false) }
            tool("", "添加滑动", icon = ToolIcon.SWIPE) { addStep(true) }
            if (plan.steps.size > 1) tool("−", "移除最后一组标记") {
                plan.steps.removeAt(plan.steps.lastIndex)
                showPanel()
            }
            tool("✓", "确定位置", 0xffa5efd6.toInt()) {
                val snapshot = plan.snapshot()
                synchronized(changes) {
                    changes[plan.id] = snapshot
                    persistChanges()
                }
                plan.data.put("points", snapshot.getJSONArray("points"))
                editing = false
                showPanel()
                if (plan.id == "__draft__") toast("点位已确认，请返回 myTools 保存方案")
            }
        } else {
            if (plan.id != "__draft__") {
                startButton = tool("▶", "开始", 0xffa5efd6.toInt()) {
                    startButton?.isEnabled = false
                    val run = ++generation
                    handler.postDelayed({ dispatch(plan, plan.count * plan.steps.size, run) }, 300L)
                }
                startButton?.isEnabled = !inFlight
                tool("■", "停止", 0xffffaba9.toInt()) { stop() }
                tool("", "调整标记", icon = ToolIcon.EDIT) { editing = true; showPanel() }
            }
            tool("", "切换方案", icon = ToolIcon.PLANS) { choosing = true; showPanel() }
        }
        if (!collapsed) {
            tool("", "隐藏连点器", icon = ToolIcon.HIDE) { collapsed = true; showPanel() }
            tool("×", "关闭") { closeControls() }
        }
        val params = overlayParams(
            WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT
        ).apply {
            gravity = Gravity.TOP or Gravity.END
            x = dp(8)
            y = dp(8)
            if (acceptsKeyboard) {
                flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
                softInputMode = WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN
            }
        }
        try {
            windows.addView(controls, params)
            panel = controls
            if (editing && !collapsed && !choosing && editingStep == null) {
                plan.steps.forEachIndexed { index, step ->
                    val label = (index + 1).toString()
                    showMarker(step.start, if (step.swipe) label + "起" else label, index)
                    if (step.swipe) showMarker(step.end, label + "终", index)
                }
            }
        } catch (_: RuntimeException) {
            closeControls()
            toast("无法显示浮窗，请检查无障碍服务")
        }
    }

    private fun createPlan() {
        val prefix = "方案 "
        var number = 1
        while (plans.values.any { it.name.trim().equals(prefix + number, ignoreCase = true) }) {
            number++
        }
        val item = JSONObject()
            .put("id", UUID.randomUUID().toString())
            .put("name", prefix + number)
            .put("action", "tap")
            .put("interval", 300).put("count", 10).put("swipeDuration", 300)
        val plan = Plan.fromJson(item)
        plans[plan.id] = plan
        selected = plan
        choosing = false
        editing = true
        showPanel()
    }

    private fun roundedBackground(fill: Int, radius: Int, border: Int = 0) = GradientDrawable().apply {
        cornerRadius = dp(radius).toFloat()
        setColor(fill)
        if (border != 0) setStroke(dp(1), border)
    }

    private fun drawToolIcon(icon: ToolIcon, tint: Int) = object : Drawable() {
        private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = tint
            strokeWidth = 1.8f
            strokeCap = Paint.Cap.ROUND
            strokeJoin = Paint.Join.ROUND
        }

        override fun draw(canvas: Canvas) {
            val scale = minOf(dp(24), bounds.width(), bounds.height()) / 24f
            canvas.save()
            canvas.translate(bounds.exactCenterX() - 12 * scale, bounds.exactCenterY() - 12 * scale)
            canvas.scale(scale, scale)
            paint.style = Paint.Style.STROKE
            when (icon) {
                ToolIcon.SHOW, ToolIcon.HIDE -> {
                    val eye = Path().apply {
                        moveTo(2f, 12f)
                        cubicTo(7f, 4f, 17f, 4f, 22f, 12f)
                        cubicTo(17f, 20f, 7f, 20f, 2f, 12f)
                        close()
                    }
                    canvas.drawPath(eye, paint)
                    canvas.drawCircle(12f, 12f, 2.8f, paint)
                    if (icon == ToolIcon.HIDE) canvas.drawLine(4f, 4f, 20f, 20f, paint)
                }
                ToolIcon.PLANS -> {
                    for (y in listOf(6f, 12f, 18f)) {
                        canvas.drawPoint(4f, y, paint)
                        canvas.drawLine(9f, y, 20f, y, paint)
                    }
                }
                ToolIcon.EDIT -> {
                    val pen = Path().apply {
                        moveTo(5f, 16f)
                        lineTo(6f, 12f)
                        lineTo(16f, 2.5f)
                        lineTo(19.5f, 6f)
                        lineTo(10f, 15.5f)
                        close()
                    }
                    canvas.drawPath(pen, paint)
                    canvas.drawLine(3.5f, 20.5f, 21f, 20.5f, paint)
                }
                ToolIcon.TAP, ToolIcon.SWIPE -> {
                    if (icon == ToolIcon.TAP) {
                        canvas.drawCircle(12f, 12f, 7f, paint)
                    } else {
                        canvas.drawLine(3f, 9f, 12f, 9f, paint)
                        canvas.drawLine(6f, 15f, 12f, 15f, paint)
                    }
                    paint.style = Paint.Style.FILL
                    canvas.drawCircle(if (icon == ToolIcon.TAP) 12f else 17f, 12f, 4f, paint)
                }
            }
            canvas.restore()
        }

        override fun setAlpha(alpha: Int) { paint.alpha = alpha; invalidateSelf() }
        override fun setColorFilter(filter: ColorFilter?) { paint.colorFilter = filter; invalidateSelf() }
        @Deprecated("Required by Drawable")
        override fun getOpacity() = PixelFormat.TRANSLUCENT
    }

    private fun overlayButton(symbol: String, label: String, tint: Int, size: Float) = Button(this).apply {
        text = symbol
        textSize = size
        isAllCaps = false
        gravity = Gravity.CENTER
        minWidth = 0
        minHeight = 0
        setPadding(0, 0, 0, 0)
        maxLines = 1
        ellipsize = android.text.TextUtils.TruncateAt.END
        contentDescription = label
        if (Build.VERSION.SDK_INT >= 26) tooltipText = label
        setTextColor(ColorStateList(
            arrayOf(intArrayOf(-android.R.attr.state_enabled), intArrayOf()),
            intArrayOf(0xff8295af.toInt(), tint)
        ))
        stateListAnimator = null
        backgroundTintList = null
        background = RippleDrawable(
            ColorStateList.valueOf(0x5578dcff),
            roundedBackground(0x683b6b99, 11),
            roundedBackground(0xffffffff.toInt(), 11)
        )
    }

    private fun overlayParams(width: Int, height: Int) = WindowManager.LayoutParams(
        width, height, WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
        WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT
    )

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()

    @Suppress("DEPRECATION")
    private fun screenSize() = Point().also { windows.defaultDisplay.getRealSize(it) }

    private fun showMarker(position: Position, label: String, index: Int) {
        val size = screenSize()
        val diameter = dp(48)
        val half = diameter / 2
        val params = overlayParams(diameter, diameter).apply {
            gravity = Gravity.TOP or Gravity.LEFT
            flags = flags or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
                WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS
            x = (position.x * (size.x - 1)).toInt() - half
            y = (position.y * (size.y - 1)).toInt() - half
        }
        val marker = overlayButton(label, "拖动标记 $label，长按设置动作", 0xffeef8ff.toInt(), 14f).apply {
            if (Build.VERSION.SDK_INT >= 26) tooltipText = null
            background = roundedBackground(0x9a102d50.toInt(), 24, 0xff78dcff.toInt())
            val slop = ViewConfiguration.get(this@ClickerService).scaledTouchSlop
            var downX = 0f
            var downY = 0f
            var originalX = 0f
            var originalY = 0f
            var moved = false
            val openSettings = Runnable {
                if (isAttachedToWindow && !moved) {
                    editingStep = index
                    showPanel()
                }
            }
            setOnTouchListener { view, event ->
                when (event.actionMasked) {
                    MotionEvent.ACTION_DOWN -> {
                        downX = event.rawX
                        downY = event.rawY
                        originalX = position.x
                        originalY = position.y
                        moved = false
                        view.postDelayed(openSettings, ViewConfiguration.getLongPressTimeout().toLong())
                        true
                    }
                    MotionEvent.ACTION_MOVE, MotionEvent.ACTION_UP -> {
                        val dx = event.rawX - downX
                        val dy = event.rawY - downY
                        if (!moved && (kotlin.math.abs(dx) > slop || kotlin.math.abs(dy) > slop)) {
                            moved = true
                            view.removeCallbacks(openSettings)
                        }
                        if (event.actionMasked == MotionEvent.ACTION_UP) view.removeCallbacks(openSettings)
                        if (!moved) return@setOnTouchListener true
                        val display = screenSize()
                        val width = (display.x - 1).coerceAtLeast(1)
                        val height = (display.y - 1).coerceAtLeast(1)
                        val x = (originalX * width + dx).coerceIn(0f, width.toFloat())
                        val y = (originalY * height + dy).coerceIn(0f, height.toFloat())
                        position.x = x / width
                        position.y = y / height
                        params.x = x.toInt() - half
                        params.y = y.toInt() - half
                        windows.updateViewLayout(view, params)
                        true
                    }
                    MotionEvent.ACTION_CANCEL -> {
                        view.removeCallbacks(openSettings)
                        true
                    }
                    else -> false
                }
            }
        }
        windows.addView(marker, params)
        markers.add(marker)
    }

    private fun stop() {
        generation++
        handler.removeCallbacksAndMessages(null)
        startButton?.isEnabled = !inFlight
    }

    private fun closeControls() {
        stop()
        markers.forEach { runCatching { windows.removeView(it) } }
        markers.clear()
        panel?.let { runCatching { windows.removeView(it) } }
        panel = null
        startButton = null
    }

    @Suppress("DEPRECATION")
    private fun dispatch(plan: Plan, remaining: Int, run: Int) {
        if (run != generation) return
        val power = getSystemService(Context.POWER_SERVICE) as PowerManager
        val keyguard = getSystemService(Context.KEYGUARD_SERVICE) as KeyguardManager
        if (!power.isInteractive || keyguard.isKeyguardLocked) {
            stop()
            return
        }
        val size = screenSize()
        val stepIndex = (plan.count * plan.steps.size - remaining) % plan.steps.size
        val step = plan.steps[stepIndex]
        val x = (size.x - 1) * step.start.x
        val y = (size.y - 1) * step.start.y
        val endX = (size.x - 1) * step.end.x
        val endY = (size.y - 1) * step.end.y
        // 目标不可落在悬浮面板内，避免模拟触摸启动或关闭面板自身。
        val location = IntArray(2)
        panel?.let { overlay ->
            overlay.getLocationOnScreen(location)
            val right = location[0] + overlay.width
            val bottom = location[1] + overlay.height
            if (minOf(x, if (step.swipe) endX else x) < right &&
                maxOf(x, if (step.swipe) endX else x) >= location[0] &&
                minOf(y, if (step.swipe) endY else y) < bottom &&
                maxOf(y, if (step.swipe) endY else y) >= location[1]) {
                stop()
                toast("触点与悬浮面板重叠，请调整坐标")
                return
            }
        }

        val path = Path().apply {
            moveTo(x, y)
            if (step.swipe) lineTo(endX, endY)
        }
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, durationOf(plan, step))).build()
        inFlight = true
        val accepted = dispatchGesture(gesture, object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) {
                inFlight = false
                if (run != generation || remaining == 1) {
                    startButton?.isEnabled = true
                } else {
                    handler.postDelayed({ dispatch(plan, remaining - 1, run) }, plan.interval)
                }
            }

            override fun onCancelled(gestureDescription: GestureDescription?) {
                inFlight = false
                if (run == generation) stop()
                else startButton?.isEnabled = true
            }
        }, null)
        if (!accepted) {
            inFlight = false
            stop()
            toast("系统未能执行手势，请检查无障碍服务")
        }
    }

    private fun durationOf(plan: Plan, step: Step) = step.duration ?: if (step.swipe) plan.duration else 45L

    private fun toast(message: String) = Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}
