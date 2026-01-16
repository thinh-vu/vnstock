# vnstock/core/utils/auth.py

"""
User authentication and API key registration for vnstock.

Simple interface for users to register their API key.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def register_user() -> bool:
    """
    Interactive user registration.
    
    Guides user through the registration process to set up their API key.
    
    Returns:
        bool: True if registration successful, False otherwise
    """
    try:
        from vnai import setup_api_key, check_api_key_status
    except ImportError:
        print("✗ Lỗi: vnai module không được tìm thấy")
        return False
    
    print("\n" + "="*70)
    print("  VNSTOCK - ĐĂNG KÝ API KEY")
    print("="*70)
    
    # Check if already registered
    try:
        status = check_api_key_status()
        if status.get('has_api_key'):
            print("\n✓ Bạn đã có API key được đăng ký")
            change = input("Bạn muốn thay đổi API key? [y/N]: ").strip().lower()
            if change != 'y':
                return True
    except Exception:
        pass
    
    print("""
Để sử dụng vnstock với giới hạn cao hơn, bạn cần đăng ký API key.

Các gói sử dụng:
  • Khách (Guest): 20 requests/phút - không cần đăng ký
  • Phiên bản cộng đồng (Community): 60 requests/phút - cần API key
  • Thành viên tài trợ (Sponsor): 180-600 requests/phút

Để lấy API key miễn phí:
  1. Truy cập: https://vnstocks.com/account
  2. Đăng ký hoặc đăng nhập bằng Google
  3. Tìm mục "API Key của bạn"
  4. Sao chép API key
""")
    
    input("Nhấn Enter khi bạn đã sao chép API key...")
    
    # Get API key from user
    max_attempts = 3
    for attempt in range(max_attempts):
        api_key = input("\nNhập API key của bạn: ").strip()
        
        if not api_key:
            print("✗ API key không được để trống")
            if attempt < max_attempts - 1:
                print(f"  Vui lòng thử lại ({max_attempts - attempt - 1} lần còn lại)")
            continue
        
        if len(api_key) < 10:
            print("✗ API key quá ngắn")
            if attempt < max_attempts - 1:
                print(f"  Vui lòng thử lại ({max_attempts - attempt - 1} lần còn lại)")
            continue
        
        # Try to save API key
        try:
            if setup_api_key(api_key):
                print("\n✓ Đăng ký thành công!")
                print("  Bạn đang sử dụng Phiên bản cộng đồng (60 requests/phút)")
                return True
        except Exception as e:
            logger.debug(f"Setup failed: {e}")
            print("✗ Không thể lưu API key")
            if attempt < max_attempts - 1:
                print(f"  Vui lòng thử lại ({max_attempts - attempt - 1} lần còn lại)")
    
    print("\n✗ Đăng ký thất bại")
    return False


def change_api_key(api_key: str) -> bool:
    """
    Change API key directly.
    
    Args:
        api_key: New API key
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not api_key or len(api_key) < 10:
        print("✗ API key không hợp lệ")
        return False
    
    try:
        from vnai import setup_api_key
        if setup_api_key(api_key):
            print("✓ API key đã được cập nhật")
            return True
    except Exception as e:
        logger.debug(f"Change failed: {e}")
        print("✗ Không thể cập nhật API key")
    
    return False


def check_status() -> Optional[dict]:
    """
    Check current registration status.
    
    Returns:
        dict: Status information or None if error
    """
    try:
        from vnai import check_api_key_status
        status = check_api_key_status()
        
        if status.get('has_api_key'):
            print(f"✓ API key: {status.get('api_key_preview')}")
            print(f"  Tier: {status.get('tier')}")
            print(f"  Giới hạn: {status.get('limits', {}).get('per_minute')} requests/phút")
        else:
            print("✗ Chưa đăng ký API key")
            print("  Tier: Guest (20 requests/phút)")
        
        return status
    except Exception as e:
        logger.debug(f"Status check failed: {e}")
        print("✗ Không thể kiểm tra trạng thái")
        return None
