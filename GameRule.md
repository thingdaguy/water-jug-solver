# Water Jug Problem (3 Jugs)

## Mô tả bài toán

Cho 3 bình chứa nước có dung tích cố định:

* Bình 1: `C1` lít
* Bình 2: `C2` lít
* Bình 3: `C3` lít

*Lưu ý: Trong dự án này, dung tích tối đa của 1 bình là 10 lít

Ban đầu tất cả các bình đều rỗng:

```text
(0, 0, 0)
```

Mục tiêu là tìm một chuỗi thao tác hợp lệ để đạt được lượng nước mong muốn `target`.

---

## Biểu diễn trạng thái

Một trạng thái được biểu diễn dưới dạng:

```text
(x1, x2, x3)
```

Trong đó:

* `x1`: lượng nước hiện có trong bình 1
* `x2`: lượng nước hiện có trong bình 2
* `x3`: lượng nước hiện có trong bình 3

Điều kiện hợp lệ:

```text
0 ≤ x1 ≤ C1
0 ≤ x2 ≤ C2
0 ≤ x3 ≤ C3
```

---

## Trạng thái khởi đầu

```text
(0, 0, 0)
```

---

## Trạng thái đích

Một trạng thái được xem là thành công nếu tồn tại ít nhất một bình chứa đúng lượng nước mục tiêu:

```text
x1 == target
OR
x2 == target
OR
x3 == target
```

Ví dụ:

Target = 4

Các trạng thái sau đều là trạng thái đích:

```text
(4,0,0)
(8,4,0)
(1,4,3)
(4,2,3)
```

---

## Các thao tác hợp lệ

### 1. Đổ đầy một bình

Đổ nước từ nguồn vô hạn vào bình cho đến khi bình đầy.

Ví dụ:

```text
(0,2,1)
→
(8,2,1)
```

---

### 2. Đổ bỏ toàn bộ nước trong một bình

Đổ hết nước trong bình ra ngoài.

Ví dụ:

```text
(8,2,1)
→
(0,2,1)
```

---

### 3. Rót nước giữa hai bình

Rót nước từ bình nguồn sang bình đích cho đến khi:

* Bình nguồn hết nước, hoặc
* Bình đích đầy.

Ví dụ:

Dung tích:

```text
(8,5,3)
```

Trạng thái:

```text
(8,2,0)
```

Rót từ bình 1 sang bình 3:

```text
(5,2,3)
```

vì bình 3 chỉ còn chứa được 3 lít.

---

## Chi phí

Mỗi thao tác hợp lệ có chi phí:

```text
cost = 1
```

Do đó:

* BFS tìm lời giải ít bước nhất.
* Greedy Best-First Search chọn trạng thái có heuristic nhỏ nhất.
* A* Search sử dụng:

```text
f(n) = g(n) + h(n)
```

Trong đó:

* `g(n)` = số bước từ trạng thái ban đầu
* `h(n)` = giá trị heuristic

---

## Đầu ra mong muốn

Chương trình cần:

1. Tìm được đường đi từ trạng thái đầu đến trạng thái đích.
2. In toàn bộ chuỗi trạng thái.
3. In số bước thực hiện.
4. In số trạng thái đã mở rộng.
5. So sánh kết quả giữa Greedy Best-First Search và A* Search.

---

## Ví dụ kiểm thử

Dung tích các bình:

```text
(8,5,3)
```

Mục tiêu:

```text
4
```

Một trạng thái đích hợp lệ:

```text
(4,4,0)
```

hoặc bất kỳ trạng thái nào có ít nhất một bình chứa đúng 4 lít.
