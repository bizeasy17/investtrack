$(function () {
    var stockmarketEndpoint = '/stockmarket/';
    var homeEndpoint = '/';
    var indexList = "sh,sz,cyb,hs300"

    $(window).keydown(function (event) {
        if ((event.keyCode == 13) && ($("#searchText").text() == "")) {
            event.preventDefault();
            return false;
        }
    });

    $('#searchText').autoComplete({
        resolver: 'custom',
        // preventEnter: true,
        formatResult: function (item) {
            return {
                value: item.id,
                text: item.id + " - " + item.text,
                html: [
                    item.id + " - " + item.text + "[" + item.market + "], " + item.area + ", " + item.industry + ", " + item.list_date + "上市",
                ]
            };
        },
        events: {
            search: function (qry, callback) {
                // let's do a custom ajax call
                $.ajax(
                    stockmarketEndpoint + 'listed_companies/' + $('#searchText').val(),
                ).done(function (res) {
                    callback(res.results)
                });
            }
        }
    });

    $('#searchText').on('autocomplete.select', function (evt, item) {
        console.log('select');
        var stockCode = item.id;
        var tsCode = item.ts_code;
        var stockName = item.text;
        var market = item.market;
        window.location.href = homeEndpoint + "?q=" + tsCode;
        // alert(
        //     tsCode + " " + stockName + " " + stockCode + " " + market
        // );
    });

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
                    } else if (obj.code == "399006") {
                        index = "cyb";
                    } else if (obj.code == "000300") {
                        index = "hs";
                    }
                    var change = Math.round((parseFloat(obj.price) - parseFloat(obj.pre_close)) / parseFloat(obj.pre_close) * 10000) / 100;
                    if (change >= 0) {
                        $("#" + index + "Change").removeClass("text-success");
                        $("#" + index + "Change").addClass("text-danger");
                        $("#" + index + "Price").removeClass("text-success");
                        $("#" + index + "Price").addClass("text-danger");
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
                    $("#" + index + "Amount").text((Math.round(parseInt(obj.amount) / 100000000)).toLocaleString() + "亿");
                    $("#" + index + "Volume").text((parseInt(obj.volume / 1000000)).toLocaleString() + "百万手");
                });
            }
        });
    }

    refreshIndex();

    // 每隔5min刷新一次
    var refreshRealtimeQ = setInterval(function () {
        var d = new Date();
        if (isOpenForTrade(d)) {
            refreshIndex();
            refreshFollowing();
        }
    }, refreshInterval * 60 * 1000);
});