---
title: "重学数据结构与算法(三): 平衡搜索二叉树-AVL树"
date: 2020-08-15
tags: ["数据结构", “算法”, “avl树", "二叉树", "树"]
categories: ['Data Structure Algorithms']
typora-root-url: ../../../static
---

## 什么是平衡二叉树(AVL 树)

AVL 树是一种自我平衡搜索二叉树(Self-banlancing binary search tree), 一共有两个要点:

1. AVL 树是一棵二叉树搜索树. 这样可以得到两个性质:
   * 选取任意一棵子树, 都有**左子结点 < 小于父结点 < 右子结点**
   * 在插入一个新的结点时, 都要从根结点这样按这个顺序比对然后才能插入, 这样的递归下来, **左树的值肯定会比右子树的小**
2. AVL 树是平衡的. 所谓平衡就是对于任意一棵子树, 其**|左子树的高度 - 右子树的高度| < 2**, 即**平衡因子**要小于 2

![avl树举例](/images/avl树举例.png "AVL 树示例")

## 插入时树的失衡与调整

当往树时插入一个结点时, 有可能会导致一棵 AVL 树不再平衡, 总结起来一共有四种失衡情况

* 左左(LL)失衡时, 要做 `右旋转(right rotation)`
* 右右(RR)失衡时, 要做 `左旋转(left rotatioin)`
* 右左(RL)失衡时, 要做 `先右旋转(right rotation), 再左旋转(left rotation)`
* 左右(LR)失衡时, 要做 `先左旋转(left rotation), 再右旋转(right rotation)`

> 一些书把这四种情况称 LL 旋转, RR 旋转, RL 旋转, LR 旋转, 但这个容易和后面解决这些失衡的操作(左旋转, 右旋转)的英文相混淆, 所以在这里记忆为**失衡**

失衡情况做旋转方便的记忆方法是

* 向**左旋转**便是**逆时针**, 向**右旋转**是**顺时针**, 这个和钟的指针方向是一样的
* 所谓左, 右失衡是指, 从失衡父结点开始算下来, 是左子结点还是右子结点
* 单旋转(RR, LL) 是要做反向的旋转, 即 R 做 L, L 做 R, 双旋转(RL, LR), 是同一样的

![树的旋转示例](/images/树的旋转示例.png "树的旋转示例，来自维基百科")


### 调整平衡步骤

1. 从叶子结点往上找到第一个平衡因子大于 2 的结点
2. 这个结点就是**失去平衡的最小子树**
3. 判断失衡类型, 也就是失衡的子树的路径
4. 调整完成, 现在这个结点下的子树已经平衡, 然后以这层开始重复第一步, 递归调整棵树的平衡

### 调整平衡要注意的要点

1. 先调整不平衡的最小子树
2. 平衡因子大于 1 的结点作为根结点

### RR 失衡(左旋转)

![RR失衡](/images/RR失衡.png "解决 RR 失衡的单左旋转")

如图的 AVL 树向其添加新的结点 ⑩, 这个结点从根开始比较, 比 ⑦ 大, 则在右树. 然后再比较右子树上的结点 ⑨, ⑩ 比 ⑨ 大, 所以结点 ⑩ 最终放在结点 ⑨ 的右子树. 这时结点 ⑦ 的左子树高度为 0, 右子树的高度为 2, 则在结点 ⑦ 的平衡因子为 2, 所以树是失衡的.

> 从失衡点 ⑦ 往下数, 导致失衡的是结点路径是右子结点 ⑨ ->右子结点  ⑩, 所以是一种 **RR(右右)失衡**, 需要做一个左旋转

右子结点 ⑨ 变成新的父结点, 原父结点 ⑦ 变左子结点, 新的父结点 ⑨ 右子树不变, 依旧是右子树, 如果原先 ⑨ 有左子结点, 那么相对 ⑨ 做一个重新插入, 因为该结点比 ⑨ 小, 比 ⑦  大, 所以一般都会成为老父子结点 ⑦  新右子结点

### LL 失衡(右旋转)

![LL失衡](/images/LL失衡.png "解决 LL 失衡的单右旋转")

如图的 AVL 树向其添加新的结点 ③, 这个结点从根开始比较, 比 ⑦ 小, 则在左子树. 然后再比较左子树上的结点 ⑤, ③ 比 ⑤ 小, 所以结点 ⑦ 最终放在结点 ⑤ 的左子树. 这时结点 ⑦ 的左子树高度为 0, 右子树的高度为 2, 则在结点 ⑦ 的平衡因子为 2, 所以树是失衡的.

> 从失衡点 ⑦ 往下数, 导致失衡的是结点路径是右子结点 ⑨ ->右子结点  ⑩, 所以是一种 **LL(左左)失衡**, 需要做一个右旋转

左子结点 ⑤ 变成新的父结点, 原父结点 ⑦ 变右子结点, 新的父结点 ⑤ 左子树不变, 依旧是左子树, 如果原先 ⑤ 有右子结点, 那么相对 ⑤ 做一个重新插入, 因为该结点比 ⑤ 大, 比 ⑦ 小, 所以一般都会成为老父子结点 ⑦  新左子结点

### RL 失衡(右旋转再左旋转)

![RL失衡](/images/RL失衡.png "解决 RL 失衡的先右旋转再左旋转")

如图的 AVL 树向其添加新的结点 ⑧, 这个结点从根开始比较, 比 ⑦ 大, 则在右子树. 然后再比较右子树上的结点 ⑨, ⑧ 比 ⑨ 小, 所以结点 ⑧ 最终放在结点 ⑨ 的左子树. 这时结点 ⑦ 的左子树高度为 0, 右子树的高度为 2, 则在结点 ⑦ 的平衡因子为 2, 所以树是失衡的.

> 从失衡点 ⑦ 往下数, 导致失衡的是结点路径是右子结点 ⑨ -> 左子结点 ⑧, 所以是一种 **RL(右左)失衡**, 需要先做一个右旋转, 然后再做一个左旋转

先以结点 ⑨ 和 ⑧ 做一个右旋转, 然后原先的三个结点 ⑦, ⑧, ⑨ 会变成 RR 失衡, 按照 RR 失衡的方法再做一个左旋转即可

### LR 失衡(左旋转再右旋转)

![LR失衡](/images/LR失衡.png "解决 LR 失衡的先左旋转再右旋转")

如图的 AVL 树向其添加新的结点 ⑥, 这个结点从根开始比较, 比 ⑦ 小, 则在左子树. 然后再比较左子树上的结点 ⑤, ⑥ 比 ⑤ 大, 所以结点 ⑥ 最终放在结点 ⑤ 的右子树. 这时结点 ⑦ 的右子树高度为 0, 左子树的高度为 2, 则在结点 ⑦ 的平衡因子为 2, 所以树是失衡的.

> 从失衡点 ⑦ 往下数, 导致失衡的是结点路径是左子结点 ⑤ -> 右子结点 ⑥, 所以是一种 **LR(左右)失衡**, 需要先做一个左旋转, 然后再做一个右旋转

先以结点 ⑤ 和 ⑥ 做一个左旋转, 然后原先的三个结点 ⑦, ⑥, ⑤ 会变成 LL 失衡, 按照 LL 失衡的方法再做一个右旋转即可

## 复杂的失衡情况举例

上面举例的出现失衡情况都是最简单的三个结点情况, 下图的情况也是一种 LL 失衡, 注意到在插入新结点 ② 后, 不平衡的结点是 ⑦, 其左树高度为 3, 右子树高度为 1, 所以平衡因子为 2. 导致结点 ⑦ 失衡原因是结点 ②, 从 ⑦ 往左子树走到 ⑤, 再下一步是左子树 ③, 所以这是一个 LL 失衡

另外一个值得注意是, 当结点 ⑤ 右转变成根结点后, 其原来的右子结点 ⑥ 变成了老根结点  ⑦ 的左子结点(替换  ⑤的位置)

>注意到新插入的结点 ② 刚好是左结点, 假如新插入结点是 ④, 则会插入到结点 ③ 的右子树, 这时依旧是一个 LL 失衡, 这种情况说明了判断失衡情况应该是从失衡结点往下相邻第一层和第二层, 第二层并不一定是新插入的结点

![LL失衡复杂情况](/images/LL失衡复杂情况.png "LL 失衡复杂情况举例")

## AVL 树生成过程举例

将数组 `{16, 3, 7, 11, 9, 26, 18, 14, 15}` 按左到右的顺序插入到 AVL 树中

![生成AVL树过程](/images/生成AVL树过程.png "生成AVL树过程")

## AVL 树代码实现

树的结点实现, 这里需要注意的是:

1. 初始化一个结点时, 设置其高度为 1, 那么其父结点就为 2, 这样每往上一层都是加 1, 空结点设为为 0
2. 对于某个结点, 其结点高度为 `max(left.height, right.height) +1`, 左右子树的高度差为 `abs(left.height - right.height)` 

```go
// 树的节点
type Node struct {
	depth int   // 该节点的深度
	val   int   // 节点数据
	left  *Node // 左子结点
	right *Node // 右子结点
}

// 比较两个结点的大小
// 相等返回 0, 小于返回 -1, 大于返回 1
func (node *Node) Equal(other *Node) int {
	if node.val == other.val {
		return 0
	} else if node.val > other.val {
		return 1
	} else {
		return -1
	}
}

type AVLTree struct {
	root *Node // 根结点
}
```

### 插入新结点

1. 我们将结点插入时, 依次递归的比较是要插入要左子结点还是右子结点, 当这个父结点没有了子结点时, 就放在该父结点的子结点位置, 代码行 19 - 23
2. 插入结点后, 新结点返回, 这时我们就要判断这个父结点的左右孩子高度差是否已经大于 1, 然后以这个为根作平衡操作
3. 之后父结点需要重新计算高度值
4. 重复第 2 步, 递归计算子树的高度值, 判断高度差是否大于 1, 决定是否需要重新平衡

```go
// 插入新数据
func (t *AVLTree) Insert(value int) {
	node := &Node{
		depth: 1,
		val:   value,
	}

	t.root = t.insertUnderNode(t.root, node)
}

func (t *AVLTree) insertUnderNode(parent *Node, newNode *Node) *Node {
	// 如果是一棵空树时, 直接返回
	// 如果该结点是已经是叶子结点, 则返回新生成的结点
	if parent == nil {
		return newNode
	}

	// 将新结点插入到左子树还是右子树
	if parent.Equal(newNode) < 0 {
		parent.right = t.insertUnderNode(parent.right, newNode)
	} else {
		parent.left = t.insertUnderNode(parent.left, newNode)
	}

	// 对比当前结点的左右子树的高度, 判断是否需要重新调整平衡
	if abs(getHeight(parent.left)-getHeight(parent.right)) > 1 {
		parent = t.makeBalance(parent)
	}

	t.calculateHeight(parent)
	return parent
}

// 计算结点高度
func (t *AVLTree) calculateHeight(node *Node) {
	left := getHeight(node.left)
	right := getHeight(node.right)
	node.depth = max(left, right) + 1
}
```

### 树的重新平衡

树的平衡主要关注的是, 我们传进来失衡的结点作为一棵子树的根结点, 我们只要关注这个结点下的直接两个子结点即可, 因为每插入一个结点都会做平衡操作, 递归回去检查平衡因子, 所以首先出现不平衡的情况就是最下方的新插入的子结点

1. 判断是什么失衡情况, 我们只要判断父结点 `parent` 直接连接下来的两棵子树的高度, 也就是

   *  父结点下**直接**的左右子树: `parent.left`(**childLeft**), `parent.right`(**childRight**)
   * 父结点下**左子树**的左右子树: `parent.left.left`(**childLeftLeft**), `parent.left.right`(**childLeftRight**)
   * 父结点下**右子树**的左右子树: `parent.rigth.left`(**childRightLeft**), `parent.right.right`(**childRightRight**)

2. LL 失衡: 左 > 右 `childLeft.height > childRight.height` && 左左 > 左右 `childLeftLeft.height > childLeftRight.height`

   * 父结点 `parent` 会变成左孩子 `childLeft` 的新的左孩子 `childLeft.left`, 所以原先这的旧的 `childLeft.left` 要给他找个新的位置
   * `childLeft` 会变成新的父结点
   * 根据二叉搜索树性质(左 < 父 < 右) 可知, `childLeftLeft` < `childLeft` < `parent`, 那么 `childLeftLeft` 放在 `parent.left` 这个位置即可, 然后我们要重新计算 parent 的高度

3. LR 失衡: 左 > 右 `childLeft.height > childRight.height` && 左右 > 左左 `childLeftRight.height > childLeftLeft.height`

   * 这个需要先做左旋再右旋, 但我们代码可以更简洁的考滤直接最终结果. 因为需要做两次旋转, 那原先最下的结点会变成新的父结点, 即是 childLeftRight => parent

   * 考虑左结点和左右结点, 从结果反推回去 `childLeftRight.left = childLeft`, 那么左右的左孩子 `childLeftRight.left` 需要先找个位置

     因为 `childLeftRight` 被提为新的父结点, 那么 `childLeft.right` 便空了出来, 便可以 `childLeft.right = childLeftRight.left`

   * 父结点会变成新父结点的右结点, 也即是 `childLeftRight.right = parent`, 那么 `childLeftRight.right` 便先需要找个地方旧的父结点的左孩子, 即是 `parent.left = childLeftRight.right`

4. RR 失衡: 右 > 左 `childLeft.height > childLeft.height` && 右右 > 右左 `childLeftRight.height > childRightLeft.height`

   这个情况和 LL 失衡是一样的, 只不过把相应的左结点改成右结点

   * 父结点 `parent` 会变成右孩子 `childRight` 的新的右孩子 `childRight.right`, 所以原先这的旧的 `childRight.right` 要给他找个新的位置

   * `childRight` 会变成新的父结点
   * 由于 `childRightRight` < `childRight` < `parent`, 那么 `childRight` 放在 `parent.right` 这个位置即可, 然后我们要重新计算 parent 的高度

5. RL 失衡: 右 > 左 `childRight.height > childLeft.height` && 右左 > 右右 `childLeftLeft.height > childRightRight.height`

   * 考虑右结点和右左结点, 从结果反推回去右结点会变成右左结点的右孩子 `childRightLeft.right = childRight`, 那么右左的右孩子 `childRightLeft.right` 需要先找个位置

     因为 `childRightLeft` 会被提为新的父结点, 那么当前 `childRifht.left` 便空了出来, 便可以 `childRight.left = childRightLeft.right`

   * 父结点会变成新父结点的左孩子, 也即是 `childRightLeft.left = parent`, 那么 `childRightLeft.left` 便先需要找个地方, 旧的父结点的右孩子, 即是 `parent.right = childLeftRightLeft.left`

> 1. 速记的方法便是, 某个结点会被提成新的父结点, 那么这个结点的原先的左孩子, 右孩子可能会变, 所以先需要找个正确的地方放置
> 2. 对于要两次旋转的, 左右孩子都会改变, 对于单次旋转的, 只有左/右孩子改变
> 3. 写代码的时候需要注意先写是后面的再写前面的, 避免被覆盖掉
> 4. 只需要重新计算改变的结点的高度, 新的父结点返回后才再计算

```go
// 以 node 为根结点的子树做平衡
func (t *AVLTree) makeBalance(node *Node) *Node {
	var node1 = node
    var node2 *Node
	if getHeight(node.left) > getHeight(node.right) &&
		getHeight(node.left.left) >= getHeight(node.left.right) {
		// ll 失衡
		node1 = node.left
		node.left = node1.right
		node1.right = node
		t.calculateHeight(node)
	} else if getHeight(node.right) > getHeight(node.left) &&
		getHeight(node.right.right) >= getHeight(node.right.left) {
		// rr 失衡
		node1 = node.right
		node.right = node1.left
		node1.left = node
		t.calculateHeight(node)
	} else if getHeight(node.left) > getHeight(node.right) &&
		getHeight(node.left.right) > getHeight(node.left.left) {
		// lr 失衡
		// 先做左旋转, 再做右旋转
		node1 = node.left.right
		node2 = node.left
		node.left = node1.right
		node2.right = node1.left
		node1.right = node
		node1.left = node2

		t.calculateHeight(node)
		t.calculateHeight(node2)
	} else if getHeight(node.right) > getHeight(node.left) &&
		getHeight(node.right.left) > getHeight(node.right.right) {
		// rl 失衡
		// 先做右旋转, 再做左旋转
		node1 = node.right.left
		node2 = node.right
		node.right = node1.left
		node2.left = node1.right
		node1.left = node
		node1.right = node2

		t.calculateHeight(node)
		t.calculateHeight(node2)
	}

	return node1
}
```

代码地址: https://github.com/ivicel/zju-data-structure

## Reference

* https://www.bilibili.com/video/BV1xE411h7dd
* https://segmentfault.com/a/1190000019101902
* https://www.bilibili.com/video/BV1Kb41127fT?p=47