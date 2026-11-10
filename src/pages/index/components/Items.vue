<template>
        <view class="box">
            <slot name="image"></slot>
            <slot></slot>
        </view>
</template>
    
<script setup lang='ts'>
    
</script>
    
<style lang="scss">
    .box{
        width:45vw;
        height: 13vh;
        background-color: pink;
        box-sizing: border-box;
        margin-top: 10rpx;
        padding: 15rpx;
        border-radius: 5px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.5s ;
        &:active{
             filter: brightness(0.9) blur(0.5px);
        }
        image {
            width: 100rpx;
        }
    }
</style>