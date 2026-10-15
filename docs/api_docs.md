Base URL: http://localhost:8000
Header xác thực: X-API-Key: training-key
API key mặc định: training-key

## 2. Endpoints Overview

| Endpoint       | Method | Resource Nghiệp vụ | Mô tả                                                             |
| :------------- | :----: | :----------------- | :---------------------------------------------------------------- |
| `/health`      | `GET`  | System Health      | Kiểm tra trạng thái hoạt động dịch vụ (không cần auth)            |
| `/customers`   | `GET`  | Customers          | Danh sách khách hàng và thông tin tài khoản                       |
| `/products`    | `GET`  | Products           | Danh mục sản phẩm, giá bán và giá vốn                             |
| `/orders`      | `GET`  | Orders             | Đơn hàng, trạng thái, kênh bán và tổng tiền                       |
| `/order-items` | `GET`  | Order Items        | Chi tiết từng dòng sản phẩm trong đơn hàng (lưu ý dấu gạch ngang) |
| `/payments`    | `GET`  | Payments           | Lịch sử giao dịch thanh toán đơn hàng                             |

## 3. Query Parameters

| Parameter       |   Kiểu    | Mặc định | Giới hạn / Định dạng                         | Mô tả                                                         |
| :-------------- | :-------: | :------: | :------------------------------------------- | :------------------------------------------------------------ |
| `page`          | `integer` |   `1`    | $\ge 1$                                      | Số thứ tự trang cần lấy dữ liệu                               |
| `page_size`     | `integer` |  `100`   | $1 \le \text{page\_size} \le 500$            | Số lượng bản ghi tối đa trên một trang                        |
| `updated_after` | `string`  |  `null`  | ISO 8601 UTC (ví dụ: `2026-07-01T12:00:00Z`) | Lọc bản ghi có `updated_at` hoặc `created_at` lớn hơn mốc này |

## 4. Response Payload Structure

```json
{
  "page": 1,
  "page_size": 10,
  "total": 600,
  "has_next": true,
  "data": [
    {
      "order_id": "ORD00000001",
      "customer_id": "CUS00000021",
      "order_date": "2026-06-25T14:20:00Z",
      "status": "completed",
      "shipping_city": "Hà Nội",
      "channel": "mobile_app",
      "order_total": 450000.0,
      "source_system": "mock_api",
      "created_at": "2026-06-25T14:20:00Z",
      "updated_at": "2026-07-01T08:30:00Z"
    }
  ]
}
```

## 5. HTTP Status Codes & Error Contract

- `200 OK`: Request thành công, dữ liệu trả về hợp lệ.
- `400 Bad Request`: Sai định dạng tham số truy vấn (ví dụ `updated_after` không đúng chuẩn ISO 8601: `{"detail": "updated_after must be ISO 8601"}`).
- `401 Unauthorized`: API key bị thiếu hoặc không chính xác (`{"detail": "Invalid API key"}`).
- `422 Unprocessable Entity`: Tham số vi phạm validation kiểu dữ liệu (ví dụ `page=0` hoặc `page_size=1000`).
