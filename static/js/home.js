$(function () {
    var chart;
    var userBaseEndpoint = '/user/';
    var investorBaseEndpoint = '/investors/';
    var investBaseEndpoint = '/invest/stocks/';
    var stockmarketEndpoint = '/stockmarket/';
    var indexList = "sh,sz,cyb"

    var refreshIndex = function () {
        $.ajax({
            url: stockmarketEndpoint + 'realtime-quotes/' + indexList + '/',
            success: function (data) {
                var index = "sh"
                $(data).each(function (idx, obj) {
                    // alert(idx);
                    if (obj.code == "000001") {
                        index = "sh";
                    } else if (obj.code == "399001") {
                        index = "sz";
                    } else {
                        index = "cyb";
                    }
                    var change = Math.round((parseFloat(obj.price) - parseFloat(obj.pre_close)) / parseFloat(obj.pre_close) * 10000) / 100;
                    if (change >= 0) {
                        $("#" + index + "Change").removeClass("text-success");
                        $("#" + index + "Change").addClass("text-danger");
                        $("#" + index + "Price").removeClass("text-success");
                        $("#" + index + "Price").addClass("text-success");
                    } else {
                        $("#" + index + "Change").addClass("text-success");
                        $("#" + index + "Change").removeClass("text-danger");
                        $("#" + index + "Price").addClass("text-success");
                        $("#" + index + "Price").removeClass("text-danger");
                    }
                    change = change + "%";
                    $("#" + index + "Change").text(change);
                    $("#" + index + "Price").text(obj.price);
                    $("#" + index + "PreClose").text(obj.pre_close);
                    $("#" + index + "Amount").text((Math.round(parseInt(obj.amount) / 100000000)).toLocaleString());
                    $("#" + index + "Volume").text((parseInt(obj.volume / 1000000)).toLocaleString());
                });
            }
        });
    }

    var refreshFollowing = function () {
        var stocks = "";
        $.ajax({
            url: investorBaseEndpoint + "stocks-following/",
            success: function (data) {
                $(data.results).each(function (idx, code) {
                    // alert(idx);   
                    stocks += code + ",";
                });

                $.ajax({
                    url: stockmarketEndpoint + 'realtime-quotes/' + stocks + '/',
                    success: function (data) {
                        var index = "sh"
                        $(data).each(function (idx, stock) {
                            var change = parseFloat(stock.price) - parseFloat(stock.pre_close);
                            var pct = Math.round((parseFloat(stock.price) - parseFloat(stock.pre_close)) / parseFloat(stock.pre_close) * 10000) / 100;
                            if (pct < 0) {
                                $("#real" + stock.code).removeClass("text-danger");
                                $("#chg" + stock.code).removeClass("text-danger");
                                $("#pct" + stock.code).removeClass("text-danger");

                                $("#real" + stock.code).addClass("text-success");
                                $("#chg" + stock.code).addClass("text-success");
                                $("#pct" + stock.code).addClass("text-success");
                            } else {
                                $("#real" + stock.code).removeClass("text-success");
                                $("#chg" + stock.code).removeClass("text-success");
                                $("#pct" + stock.code).removeClass("text-success");

                                $("#real" + stock.code).addClass("text-danger");
                                $("#chg" + stock.code).addClass("text-danger");
                                $("#pct" + stock.code).addClass("text-danger");
                            }
                            $("#real" + stock.code).text(stock.price);
                            $("#chg" + stock.code).text(change.toFixed(2));
                            $("#pct" + stock.code).text(pct.toString() + "%");
                            // if (change >= 0) {
                            //     $("#" + index + "Change").removeClass("text-success");
                            //     $("#" + index + "Change").addClass("text-danger");
                            //     $("#" + index + "Price").removeClass("text-success");
                            //     $("#" + index + "Price").addClass("text-success");
                            // } else {
                            //     $("#" + index + "Change").addClass("text-success");
                            //     $("#" + index + "Change").removeClass("text-danger");
                            //     $("#" + index + "Price").addClass("text-success");
                            //     $("#" + index + "Price").removeClass("text-danger");
                            // }
                            // change = change + "%";
                            // $("#" + index + "Change").text(change);
                            // $("#" + index + "Price").text(obj.price);
                            // $("#" + index + "PreClose").text(obj.pre_close);
                            // $("#" + index + "Amount").text((Math.round(parseInt(obj.amount) / 100000000)).toLocaleString());
                            // $("#" + index + "Volume").text((parseInt(obj.volume / 1000000)).toLocaleString());
                        });
                    }
                });
            }
        });
    }

    refreshIndex();
    refreshFollowing();

    // 每隔5min刷新一次
    var refreshRealtimeQ = setInterval(function () {
        var d = new Date();
        if (isOpenForTrade(d)) {
            refreshIndex();
            refreshFollowing();
        }
    }, refreshInterval * 60 * 1000);
});