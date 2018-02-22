Title: Interpolator值
Date: 2018-02-22
Tags: android, interpolator



- AccelerateDecelerateInterpolator 动画从开始到结束，变化率是先加速后减速的过程。
- AccelerateInterpolator 动画从开始到结束，变化率是一个加速的过程。
- AnticipateInterpolator 开始的时候向后，然后向前甩
- AnticipateOvershootInterpolator 开始的时候向后，然后向前甩一定值后返回最后的值
- BounceInterpolator 动画结束的时候弹起
- CycleInterpolator 动画从开始到结束，变化率是循环给定次数的正弦曲线。
- DecelerateInterpolator 动画从开始到结束，变化率是一个减速的过程。
- LinearInterpolator 以常量速率改变
- OvershootInterpolator 向前甩一定值后再回到原来位置

