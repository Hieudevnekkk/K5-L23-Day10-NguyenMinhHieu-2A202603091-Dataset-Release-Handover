# Bảo mật khi làm việc

> Trả lời gắn với lô r24007 (seed 24007, 250 ảnh COCO) mà nhóm vừa bàn giao.

## 1. Ca USB: hết giờ, muốn chép lô về nhà làm tiếp

Không chép. Lô v1 và các ảnh trong `runs/r24007/delivery/` nằm trong vùng kiểm soát của công ty; chép ra USB là đưa dữ liệu ra khỏi chỗ có phân quyền và nhật ký truy cập, mất USB thì không thu hồi được. Gửi qua email cá nhân hay nhờ người khác làm hộ cũng sai vì cùng lý do: dữ liệu sang một nơi không có kiểm soát, và người nhận không nằm trong danh sách được giao job, không ký cam kết bảo mật. Cách đúng: báo người phụ trách rằng chưa kịp xong, xin gia hạn hoặc xin thêm giờ làm trên máy công ty, hoặc xin được cấp quyền làm việc từ xa qua kênh công ty cho phép (VPN, máy ảo). Ghi rõ phần đã xong và phần còn lại vào bàn giao để người khác nối tiếp trong hệ thống.

## 2. Năm việc: được hay không

- **Mở job được giao trên máy công ty: được.** Đúng người được giao, đúng thiết bị, đúng nơi; truy cập được ghi nhận.
- **Chụp màn hình gửi người quen: không.** Ảnh trong lô có người thật (ví dụ ảnh cận mặt `000000023034`), gửi ra ngoài là lộ dữ liệu của người trong ảnh và của khách hàng; ảnh chụp màn hình cũng nằm ngoài mọi nhật ký kiểm soát.
- **Chép lô ra USB: không**, trừ khi có phê duyệt bằng văn bản của người phụ trách. Lý do như ca 1.
- **Dán nhãn thật lên chatbot: không.** Nhãn và ảnh bị gửi cho bên thứ ba, có thể bị lưu hoặc dùng để huấn luyện, và không thu hồi được. Muốn dùng AI thì dùng dữ liệu giả hoặc tóm tắt không chứa dữ liệu thật, và ghi vào `prompts.md`.
- **Đưa tài khoản CVAT cho đồng nghiệp: không.** Tài khoản gắn với một người; dùng chung làm mất truy vết người gán và người kiểm (chính thông tin ta cần để báo đúng người ở Pha 5). Đồng nghiệp cần quyền thì xin người phụ trách cấp tài khoản riêng.

## 3. Ca khuôn mặt: thấy mặt người rõ trong lô, guideline yêu cầu làm mờ

Trạng thái lô: **Hold**. Mình dừng không phát hành lô và báo ngay người phụ trách (trưởng nhóm hoặc người phụ trách dữ liệu và quyền riêng tư), nêu cụ thể ảnh đã thấy. Trong lô r24007 có ảnh người nhìn rõ mặt: `000000023034` (cận cảnh một người đội mũ cam đeo ba lô) và `000000012748` (người lớn và em bé được bế, thấy rõ mặt).

Không tự làm mờ hay xoá ảnh vì: (1) v1 phải giữ nguyên để hash trong `manifest.json` và `lineage.jsonl` còn đúng; sửa hay xoá ảnh làm đổi `release_id` và mất truy vết, mà đó không phải việc của người QC; (2) quyết định làm mờ, xoá hay loại ảnh khỏi lô thuộc người phụ trách theo chính sách quyền riêng tư, kèm ghi nhận để lần sau áp dụng đồng nhất; (3) xoá nhầm có thể mất dữ liệu không khôi phục được. Sau khi người phụ trách quyết định, việc xử lý được làm ở lô v2, có parent là v1 và có manifest mới.
