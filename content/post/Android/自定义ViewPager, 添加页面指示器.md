---

Title: "Android 中自定义ViewPager, 添加页面指示器"
Date: 2018-02-22
Tags: ["android", "viewpager", "页面指示器"]

---



- 在页面滑动时会回调`ViewPager.OnPageChangeListener`接口里的方法. 用`ViewPage.addOnPageChangeListener`添加和`ViewPage.removeOnPageChangeListener`删除监听回调方法. 如果不想实现所有方法, `ViewPager`内有个空的类`SimpleOnPageChangeListener`实现了这个接口, 继承这个类便可. **注意可以多次调用`addOnPageChangeListener`方法添加多个回调, `ViewPager`按添加顺序进行调用, 所以在不需要回调时, 及时的使用`removeOnPageChangeListener`来删除回调方法**. 另外还需要**注意的是`ViewPager.getCurrentItem`返回值和`OnPageSelected`参数是一样的, 即是成功滑动后的目标页面索引, 无论当前页面是否还在滑动中**

  1. 在滑动的时候会调用`OnPageScrolled(int position, float positionOffset, int positionOffsetPixels)`

     - 参数`position`指的是在滑动时**当前显示页面**的**左边页面的位置**, 具体来说是

     > *i.* 在**向右**滑动时, `position`的值为当前页面的值, 如果滑动成功(即滑动到右一页面), `OnPageScrolled`会被再一次调用, 此时`position`的值为滑动成功后的页面`position+1`, 如果滑动失败, `position`依然不变
     >
     >  	从 `0`滑动`1`时, 滑动时`position`是`0`, 滑动成功后`OnPageScrolled`会再被调用一次且`position`会变成`1`, 滑动失败`position`依然为`0`, 这跟向左滑动有区别, 需要注意
     >
     > *ii.* 在**向左**滑动时, `position`的值为滑动的目标页面, 滑动成功后, 不会再次调用`OnPageScrolled`. 如果滑动失败, 最后一次会再次调用`OnPageScrolled`, 此时`position`为原先页面.
     >
     > ​	 从`1`滑动到`0`时, `position`的值为`0`, 成功滑动到页面`1`后也不会再次调用该方法, 这个有区别于向右滑动. 然而如果滑动失败, 则会再一次调用该方法, 此时`position`的值为`1`

     - 参数`positionOffset`指的是滑动时, `index`为`position + 1`的页面占显示窗口(`ViewPager`)的百分比, 其取值为`[0, 1)`, 当值为`0`时, 页面停止滑动. 

     > *i.* 向右滑动时, `positionOffset`从`0`变大到接近`1`(不包含), 最后变成`0`(滑动停止时)
     >
     > *ii.* 向左滑动时, `positionOffset`从`1`(不包含)变小到`0`(当为`0`时已经停止滑动)

     - `positionOffsetPixels`指的是滑动像素值, 情况和`positionOffset`是一致的. 

     > *i.* 向右滑动, `positionOffsetPixels`一直增大到和显示窗口(`ViewPager`)一样, 滑动停止时变为`0`
     >
     > *ii.* 向左滑动, `positionOffsetPixels`从窗口大小一直减小到`0`

  2. `OnPageSelected(int position)` 

     该方法会在滑动成功时立即被调用, 滑动成功的意思指手指在滑动页面**足够长**的距离后, 手指离开屏幕的一瞬间, 屏幕会自行滑动到目标页面即为滑动成功; 如果**距离不够**, 页面会回弹, 即为滑动失败. `OnPageSelected`会在滑动成功的瞬间立即被调用, 无论当前页面是否还在滑动中. `position`指的是目标页面的索引值. **注意`OnPageSelected`在调用时, `OnPageScrolled`可能会还在继续被调用中**

  3. `OnPageScrollStateChanged(int state)`

     该方法在页面状态有改变时会调用, `state`指当前页面的状态, 一共有三个状态. 

     > *i.* `ViewPager.SCROLL_STATE_DRAGGING` 页面在拖拽, 值为`1`
     >
     > *ii.* `ViewPager.SCROLL_STATE_SETTLING` 手指离开屏幕, 页面正滑向目标页面, 值为`2`
     >
     > *iii.* `ViewPager.SCROLL_STATE_IDLE` 页面空闲中, 无任何滑动拖拽动画, 值为`0`

     页面的状态总是会经历`1`,  `2`,  `0`的顺序状态, 手指按到屏幕时, 状态为`1`, 手指离开屏幕时, 状态为`2`, 页面无任何动画时, 状态为`0`




##### Reference:

1. http://dalufan.com/2015/09/08/android-setOnPageChangeListener/