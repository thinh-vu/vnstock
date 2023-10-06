/**
 * Get derivatives historical price from DNSE.
 *
 * @param {string} ticker Derivative symbol.
 * @param {string} from_date Start date of historical price data in the format 'YYYY-MM-DD'.
 * @param {string} to_date End date of historical price data in the format 'YYYY-MM-DD'.
 * @param {string} resolution Resolution of historical price data. Default is '1D' (daily).
 * @return {Array} An array containing historical price data.
 * @customfunction
 */
function derivativesOhlc(ticker="VN30F1M", from_date="2023-09-01", to_date="2023-09-10", resolution="1D") {
  // Parse from_date and to_date to timestamps
  var fromTimestamp = Date.parse(from_date) / 1000; // Convert to seconds
  var toTimestamp = Date.parse(to_date) / 1000; // Convert to seconds
  // Logger.log(fromTimestamp, toTimestamp)

  // Create the URL
  var url = "https://services.entrade.com.vn/chart-api/v2/ohlcs/derivative?" +
    "from=" + fromTimestamp +
    "&to=" + toTimestamp +
    "&symbol=" + ticker +
    "&resolution=" + resolution;

  // Make an HTTP GET request
  var response = UrlFetchApp.fetch(url);
  var responseData = JSON.parse(response.getContentText());

  Logger.log(responseData)
  // Process the data
  var ohlcData = [];
  for (var i = 0; i < responseData.t.length; i++) {
    var timestamp = new Date(responseData.t[i] * 1000) //.toISOString();
    // Convert timestamp to Asia/Ho_Chi_Minh timezone
    var tzTimestamp = Utilities.formatDate(timestamp, "Asia/Ho_Chi_Minh", "yyyy-MM-dd HH:mm:ss");
    var open = responseData.o[i];
    var high = responseData.h[i];
    var low = responseData.l[i];
    var close = responseData.c[i];
    var volume = responseData.v[i];
    ohlcData.push([tzTimestamp, open, high, low, close, volume]);
  }

  // Add headers
  var headers = ["Time", "Open", "High", "Low", "Close", "Volume"];
  ohlcData.unshift(headers);
  return ohlcData
}
