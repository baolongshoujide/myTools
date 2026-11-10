<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
onLaunch(() => {
  console.log("App Launch");
});
onShow(() => {
  console.log("App Show");
  uni.onTabBarMidButtonTap(()=>{
  console.log('中间按钮被点击了')
})
});
onHide(() => {
  console.log("App Hide");
});

</script>
<style lang="scss">
page{
  padding: 0;
  margin: 0;
  box-sizing: border-box;
}
</style>
