import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from vnstock.explorer.fmarket.fund import Fund, convert_unix_to_datetime

class TestFund(unittest.TestCase):

    def setUp(self):
        self.fund = Fund(random_agent=True)
        self.short_names = [
            'SSISCA', 'VESAF', 'BVPF', 'VEOF', 'VCBF-TBF', 'VCBF-BCF', 'VFF', 'PVBF', 'VNDBF',
            'VCBF-FIF', 'VCAMBF', 'VIBF', 'ABBF', 'DCBF', 'SSIBF', 'DCDS', 'MAGEF', 'MBBOND',
            'BVBF', 'MBVF', 'DCIP', 'VNDAF', 'DFIX', 'MAFBAL', 'DCDE', 'MAFEQI', 'BVFED', 'DCAF',
            'VMEEF', 'VLGF', 'VCBF-MGF', 'UVEEF', 'PHVSF', 'TBLF', 'HDBOND', 'VCAM-NH VABF',
            'MAFF', 'LHBF', 'ASBF', 'NTPPF', 'VNDCF', 'VLBF', 'PBIF', 'VDEF', 'TCGF', 'UVDIF',
            'MDI', 'LHCDF', 'VCAMDF'
        ]

    @patch('vnstock.explorer.fmarket.fund.requests.post')
    def test_listing_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "total": 10,
                "rows": [
                    {
                        "shortName": "SSISCA", 
                        "name": "QUỸ ĐẦU TƯ LỢI THẾ CẠNH TRANH BỀN VỮNG SSI", 
                        "dataFundAssetType.name": "Quỹ cổ phiếu", 
                        "owner.name": "CÔNG TY TNHH QUẢN LÝ QUỸ SSI", 
                        "managementFee": 1.75, 
                        "firstIssueAt": 1411603200000,
                        "nav": 40055.9, 
                        "productNavChange.navToPrevious": 0.46, 
                        "productNavChange.navToLastYear": 31.01, 
                        "productNavChange.navToBeginning": 177.93, 
                        "productNavChange.navTo1Months": 2.6, 
                        "productNavChange.navTo3Months": 13.61, 
                        "productNavChange.navTo6Months": 27.83, 
                        "productNavChange.navTo12Months": 41.96, 
                        "productNavChange.navTo24Months": 44.61, 
                        "productNavChange.annualizedReturn36Months": 11.69, 
                        "id": 11, 
                        "code": "SSISCA", 
                        "vsdFeeId": "SSISCAN001",
                        "productNavChange.updateAt": 1688880000000
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        result = self.fund.listing()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('short_name', result.columns)
        self.assertEqual(result.iloc[0]['short_name'], 'SSISCA')

        expected_result = pd.DataFrame([{
            'short_name': 'SSISCA',
            'name': 'QUỸ ĐẦU TƯ LỢI THẾ CẠNH TRANH BỀN VỮNG SSI',
            'fund_type': 'Quỹ cổ phiếu',
            'fund_owner_name': 'CÔNG TY TNHH QUẢN LÝ QUỸ SSI',
            'management_fee': 1.75,
            'inception_date': '2014-09-25',
            'nav': 40055.9,
            'nav_change_previous': 0.46,
            'nav_change_last_year': 31.01,
            'nav_change_inception': 177.93,
            'nav_change_1m': 2.6,
            'nav_change_3m': 13.61,
            'nav_change_6m': 27.83,
            'nav_change_12m': 41.96,
            'nav_change_24m': 44.61,
            'nav_change_36m': 39.34,
            'nav_change_36m_annualized': 11.69,
            'nav_update_at': '2024-07-09',
            'fund_id_fmarket': 11,
            'fund_code': 'SSISCA',
            'vsd_fee_id': 'SSISCAN001'
        }])
        pd.testing.assert_frame_equal(result, expected_result)

    @patch('vnstock.explorer.fmarket.fund.requests.post')
    def test_filter_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "rows": [
                    {"id": 23, "shortName": "SSISCA"}
                ]
            }
        }
        mock_post.return_value = mock_response

        result = self.fund.filter(symbol='SSISCA')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.iloc[0]['shortName'], 'SSISCA')

    @patch('vnstock.explorer.fmarket.fund.requests.post')
    def test_filter_no_results(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "rows": []
            }
        }
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            self.fund.filter(symbol='INVALID')

    @patch('vnstock.explorer.fmarket.fund.requests.get')
    @patch('vnstock.explorer.fmarket.fund.Fund.filter')
    def test_top_holding_success(self, mock_filter, mock_get):
        mock_filter.return_value = pd.DataFrame([{"id": 23}])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "productTopHoldingList": [
                    {"stockCode": "FPT", "industry": "Công nghệ và thông tin", "netAssetPercent": 17.1, "type": "STOCK", "updateAt": 1688784000000},
                    {"stockCode": "MWG", "industry": "Bán lẻ", "netAssetPercent": 6.65, "type": "STOCK", "updateAt": 1688784000000},
                    # More data as needed
                ],
                "productTopHoldingBondList": []
            }
        }
        mock_get.return_value = mock_response

        result = self.fund.details.top_holding(symbol='SSISCA')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('stock_code', result.columns)
        self.assertEqual(result.iloc[0]['stock_code'], 'FPT')

        expected_result = pd.DataFrame([
            {"stock_code": "FPT", "industry": "Công nghệ và thông tin", "net_asset_percent": 17.1, "type_asset": "STOCK", "update_at": "2024-07-05", "fundId": 23, "short_name": "SSISCA"},
            {"stock_code": "MWG", "industry": "Bán lẻ", "net_asset_percent": 6.65, "type_asset": "STOCK", "update_at": "2024-07-05", "fundId": 23, "short_name": "SSISCA"}
        ])
        pd.testing.assert_frame_equal(result, expected_result)

    @patch('vnstock.explorer.fmarket.fund.requests.get')
    @patch('vnstock.explorer.fmarket.fund.Fund.filter')
    def test_top_holding_missing_columns(self, mock_filter, mock_get):
        mock_filter.return_value = pd.DataFrame([{"id": 23}])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "productTopHoldingList": [
                    {"updateAt": 1688784000000, "netAssetPercent": 0.1, "type": "STOCK"}
                ],
                "productTopHoldingBondList": []
            }
        }
        mock_get.return_value = mock_response

        result = self.fund.details.top_holding(symbol='SSISCA')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('update_at', result.columns)
        self.assertNotIn('stock_code', result.columns)  # stock_code is missing in mock data

    def test_dynamic_fund_short_names(self):
        for short_name in self.short_names:
            with patch('vnstock.explorer.fmarket.fund.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "data": {
                        "total": 10,
                        "rows": [
                            {
                                "shortName": short_name,
                                "name": "Dynamic Fund Name",
                                "dataFundAssetType.name": "Dynamic Fund Type",
                                "owner.name": "Dynamic Fund Owner",
                                "managementFee": 1.5,
                                "firstIssueAt": 1411603200000,
                                "nav": 10000.0,
                                "productNavChange.navToPrevious": 0.1,
                                "productNavChange.navToLastYear": 10.0,
                                "productNavChange.navToBeginning": 50.0,
                                "productNavChange.navTo1Months": 1.0,
                                "productNavChange.navTo3Months": 5.0,
                                "productNavChange.navTo6Months": 7.5,
                                "productNavChange.navTo12Months": 12.0,
                                "productNavChange.navTo24Months": 20.0,
                                "productNavChange.annualizedReturn36Months": 8.0,
                                "id": 1,
                                "code": short_name,
                                "vsdFeeId": "DynamicVSD001",
                                "productNavChange.updateAt": 1688880000000
                            }
                        ]
                    }
                }
                mock_post.return_value = mock_response

                result = self.fund.listing()
                self.assertIsInstance(result, pd.DataFrame)
                self.assertIn('short_name', result.columns)
                self.assertEqual(result.iloc[0]['short_name'], short_name)

if __name__ == '__main__':
    unittest.main()
