# Tích hợp API giao dịch DNSE vào vnstock

!!! abstract "DNSE API" 
    DNSE là một trong 3 công ty chứng khoán có cung cấp API giao dịch cho khách hàng phổ thông bên cạnh SSI và BSC (đang kiểm duyệt kỹ, không duyệt thêm khách hàng mới).
    API giao dịch của DNSE cho phép thực hiện đọc thông tin liên quan đến tài khoản và đặt lệnh đối với cả giao dịch cơ sở lẫn phái sinh. Tài liệu API thường được chia sẻ qua các nhóm hỗ trợ,  thông tin này không tìm thấy qua tìm kiếm kiếm Google hay trên website. Bạn có thể tham khảo thông tin API giao dịch chi tiết [tại đây](https://drive.google.com/file/d/1nRQzJxb4E-SxhE-6Znt0IZLvAVoaPCiB/view)

Dưới đây, vnstock cung cấp demo về cách kết nối với hệ thống DNSE, trước tiên bạn sẽ cần cài đặt gói thư viện vnstock để sử dụng tất cả các hàm kèm theo một cách dễ dàng. Xem thêm [mã nguồn](https://github.com/thinh-vu/vnstock/blob/beta/vnstock/integration.py) để lấy cảm hứng.

[Xem hướng dẫn :material-rocket-launch:](../start/start.md){ .md-button }

## Lấy mã JWT Token

!!! info "JWT token"
    JWT token là mã xác thực được tạo ra khi bạn đăng nhập vào hệ thống API của DNSE. Mã này cho phép bạn đọc các thông tin về tài khoản (Xác thực cấp 1), để thực hiện đặt lệnh, sửa thông tin hệ thống thì cần dùng kết hợp với mã OTP được cấp qua email hoặc SmartOTP trên app EntradeX.

Để lấy mã token này, các bạn sử dụng câu lệnh sau:

```
from vnstock.integration import *
token = dnse_login(user_name='USER_NAME_CỦA_BẠN', password='MẬT_KHẨU_CỦA_BẠN')
```

Kết quả là JWT token sẽ được gán vào biến token để sử dụng trong các bước tiếp theo.

## Thông tin tài khoản

Để đến được bước này, bạn đã trải qua bước tạo token, do đó không cần nạp lại thư viện mà chạy code trực tiếp

```
dnse_profile(token)
```

Kết quả trả về như sau:

```shell
>>> dnse_profile(token)
id                                                                0123456789
investorId                                                        0123456789
name                                                            	Vũ Thịnh
custodyCode                                                        064C12345
email                                                   support@vnstock.site
unverifiedEmail                                         support@vnstock.site
mobile                                                            0123456789
status                                                                ACTIVE
createdDate                                         2023-01-01T00:00:00.007Z
modifiedDate                                        2023-01-01T00:00:00.007Z
enId                                        xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx
identificationCode                                          0123456789010101
identificationDate                                      2021-01-01T00:00:00Z
identificationExpiredDate                               2100-01-01T00:00:00Z
identificationPlace                                      Cục CS QLHC về TTXH
birthday                                                XXXX-XX-XXT00:00:00Z
address                                   vnstock chào đón các nhà đầu tư 😁
gender                                                                  MALE
flexCustomerId                                                    000000000
smartOtpRegistrationId                                               xxxxx
userApproveType                                                AUTO_APPROVED
referralCode                                                          xxxxxx
referralUrl                                         https://s.dnse.vn/xxxxxx
avatarUrl                           https://lh3.googleusercontent.com/xyzxyz
needToChangePassword                                                   True
registeredSmartOtp                                                     False
isEmailVerified                                                        False
```

