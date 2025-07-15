import unittest
from unittest.mock import patch, MagicMock
from vnstock.core.utils import client

class TestClientUtils(unittest.TestCase):
    def setUp(self):
        self.url = "https://example.com/api"
        self.headers = {"Authorization": "Bearer testtoken"}
        self.proxy_list = ["http://proxy1.com", "http://proxy2.com"]
        self.payload = {"key": "value"}

    @patch("vnstock.core.utils.client.requests.get")
    def test_send_request_direct_get(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"result": "ok"}
        result = client.send_request_direct(self.url, self.headers)
        self.assertEqual(result, {"result": "ok"})

    @patch("vnstock.core.utils.client.requests.post")
    def test_send_request_direct_post(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "posted"}
        result = client.send_request_direct(self.url, self.headers, method="POST", payload=self.payload)
        self.assertEqual(result, {"result": "posted"})

    def test_get_proxy_by_mode_single(self):
        proxy = client.get_proxy_by_mode(self.proxy_list, client.ProxyMode.SINGLE)
        self.assertEqual(proxy, self.proxy_list[0])

    def test_get_proxy_by_mode_random(self):
        proxy = client.get_proxy_by_mode(self.proxy_list, client.ProxyMode.RANDOM)
        self.assertIn(proxy, self.proxy_list)

    def test_get_proxy_by_mode_rotate(self):
        client.reset_proxy_rotation()
        proxy1 = client.get_proxy_by_mode(self.proxy_list, client.ProxyMode.ROTATE)
        proxy2 = client.get_proxy_by_mode(self.proxy_list, client.ProxyMode.ROTATE)
        self.assertNotEqual(proxy1, proxy2)
        self.assertIn(proxy1, self.proxy_list)
        self.assertIn(proxy2, self.proxy_list)

    def test_build_proxy_dict(self):
        proxy_url = "http://proxy.com"
        proxy_dict = client.build_proxy_dict(proxy_url)
        self.assertEqual(proxy_dict, {"http": proxy_url, "https": proxy_url})

    def test_create_hf_proxy_payload(self):
        payload = client.create_hf_proxy_payload(self.url, self.headers, "POST", self.payload)
        self.assertEqual(payload["url"], self.url)
        self.assertEqual(payload["headers"], self.headers)
        self.assertEqual(payload["method"], "POST")
        self.assertEqual(payload["payload"], self.payload)

    @patch("vnstock.core.utils.client.send_request_direct")
    def test_send_request_hf_proxy(self, mock_send_direct):
        mock_send_direct.return_value = {"result": "hf_proxy"}
        result = client.send_request_hf_proxy(self.url, self.headers, method="GET", params={"a":1}, payload=None, hf_proxy_url="http://hfproxy.com")
        self.assertEqual(result, {"result": "hf_proxy"})

    @patch("vnstock.core.utils.client.send_request_direct")
    def test_send_request_proxy_mode(self, mock_send_direct):
        mock_send_direct.return_value = {"result": "proxy"}
        result = client.send_proxy_request(self.url, self.headers, self.proxy_list)
        self.assertEqual(result, {"result": "proxy"})

    @patch("vnstock.core.utils.client.send_request_hf_proxy")
    def test_send_hf_proxy_request(self, mock_hf_proxy):
        mock_hf_proxy.return_value = {"result": "hf_proxy"}
        result = client.send_hf_proxy_request(self.url, self.headers)
        self.assertEqual(result, {"result": "hf_proxy"})


class TestClientHFProxyReal(unittest.TestCase):
    def setUp(self):
        self.hf_proxy_url = "https://autonomous-it-proxy-vci.hf.space/proxy"
        self.target_url = "https://httpbin.org/get"
        self.headers = {"Accept": "application/json"}

    def test_real_hf_proxy_get(self):
        # Gửi request thực qua HF proxy tới httpbin.org
        result = client.send_request_hf_proxy(
            url=self.target_url,
            headers=self.headers,
            method="GET",
            params={"test": "hf"},
            hf_proxy_url=self.hf_proxy_url
        )
        # Kết quả trả về phải có trường 'url' và đúng endpoint
        self.assertIn("url", result)
        self.assertTrue(result["url"].startswith(self.target_url))

if __name__ == "__main__":
    unittest.main()
