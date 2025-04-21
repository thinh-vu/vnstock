name: Báo lỗi
description: Tạo báo lỗi giúp tác giả phát hiện và sửa lỗi nhanh chóng
title: "[Bug]: "
labels: ["bug"]
projects:
  - 4
assignees:
  - thinh-vu
body:
  - type: markdown
    attributes:
      value: |
        Cảm ơn bạn đã dành thời gian báo cáo lỗi này!
  - type: textarea
    id: bug-description
    attributes:
      label: Mô tả lỗi
      description: Mô tả một cách rõ ràng và ngắn gọn về lỗi.
      placeholder: Vui lòng mô tả chi tiết lỗi bạn gặp phải...
    validations:
      required: true
  - type: textarea
    id: reproduction-steps
    attributes:
      label: Cách tái hiện lại lỗi để xử lý
      description: Các bước để tái hiện sự cố
      placeholder: |
        1. Sử dụng VSCode '...'
        2. Sử dụng hàm '....'
        3. Thực thi lệnh '....'
        4. Gặp lỗi
    validations:
      required: true
  - type: textarea
    id: expected-behavior
    attributes:
      label: Mong muốn đạt được
      description: Mô tả một cách rõ ràng và ngắn gọn về kỳ vọng của bạn.
      placeholder: Mô tả kết quả bạn mong muốn đạt được...
    validations:
      required: true
  - type: textarea
    id: screenshots
    attributes:
      label: Ảnh chụp màn hình
      description: Nếu có, hãy thêm ảnh chụp màn hình để giúp giải thích vấn đề của bạn.
      placeholder: Kéo và thả ảnh chụp màn hình vào đây...
    validations:
      required: false
  - type: dropdown
    id: operating-system
    attributes:
      label: Hệ điều hành
      description: Bạn đang sử dụng hệ điều hành nào?
      options:
        - Windows
        - macOS
        - Linux
        - Khác
    validations:
      required: true
  - type: dropdown
    id: environment
    attributes:
      label: Môi trường
      description: Bạn đang sử dụng trong môi trường nào?
      options:
        - VSCode
        - Jupyter Notebook
        - Google Colab
        - PyCharm
        - Khác
    validations:
      required: true
  - type: input
    id: version
    attributes:
      label: Phiên bản
      description: Phiên bản phần mềm bạn đang sử dụng
      placeholder: ví dụ 1.0.9
    validations:
      required: true
  - type: input
    id: python-version
    attributes:
      label: Phiên bản Python
      description: Phiên bản Python bạn đang sử dụng
      placeholder: ví dụ 3.11.3
    validations:
      required: true
  - type: dropdown
    id: virtual-env
    attributes:
      label: Môi trường ảo
      description: Bạn có sử dụng môi trường ảo không?
      options:
        - Có
        - Không
    validations:
      required: true
  - type: textarea
    id: logs
    attributes:
      label: Thông báo lỗi hoặc logs
      description: Sao chép và dán bất kỳ thông báo lỗi hoặc logs nào liên quan.
      render: shell
    validations:
      required: false
  - type: checkboxes
    id: terms
    attributes:
      label: Xác nhận
      options:
        - label: Tôi đã kiểm tra thông tin và xác nhận lỗi này chưa được báo cáo trước đây
          required: true
