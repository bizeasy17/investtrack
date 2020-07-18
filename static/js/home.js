$(function () {
    var chart;
    var userBaseEndpoint = '/user/';
    var dashboardEndpoint = '/dashboard/';
    var investorBaseEndpoint = '/investors/';
    var investBaseEndpoint = '/invest/stocks/';
    var stockmarketEndpoint = '/stockmarket/';
    var indexList = "sh,sz,cyb"
    var chartCanvas = document.getElementById('stockChart').getContext('2d');

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
                        });
                    }
                });
            }
        });
    }

    if ($("#positionChart").length) {
        var positionChartCanvas = $("#positionChart").get(0).getContext("2d");
        var account = 'a'; //all account
        var stock_symbol = 'a'; //all stock shares
        $.ajax({
            url: dashboardEndpoint + 'position-vs-status/' + account + '/' + stock_symbol + '/',
            // headers: { 'X-CSRFToken': csrftoken },
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data.code == "empty") {
                    $("#noPosition").append("<span class='text-muted'>无持仓信息</span>");
                } else {
                    $("#pTotalAvailPerTarget").text(data.total_percentage);
                    var positionChart = new Chart(positionChartCanvas, {
                        type: 'horizontalBar',
                        data: {
                            labels: data.label,
                            datasets: [
                                {
                                    label: '目标仓位',
                                    data: data.target_position,
                                    backgroundColor: '#1cbccd',
                                },
                                {
                                    label: '已有仓位',
                                    data: data.available_position,
                                    backgroundColor: '#ffbf36',
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            layout: {
                                padding: {
                                    left: -7,
                                    right: 0,
                                    top: 0,
                                    bottom: 0
                                }
                            },
                            scales: {
                                yAxes: [{
                                    display: true,
                                    gridLines: {
                                        display: false,
                                        drawBorder: false
                                    },
                                    ticks: {
                                        display: true,
                                        min: 0,
                                        max: 400,
                                        stepSize: 100,
                                        fontColor: "#b1b0b0",
                                        fontSize: 10,
                                        padding: 10
                                    },
                                }],
                                xAxes: [{
                                    display: true,
                                    stacked: false,
                                    ticks: {
                                        display: false,
                                        beginAtZero: true,
                                        fontColor: "#b1b0b0",
                                        fontSize: 10
                                    },
                                    gridLines: {
                                        display: true,
                                        drawBorder: false,
                                        lineWidth: 1,
                                        color: "#f5f5f5",
                                        zeroLineColor: "#f5f5f5"
                                    }
                                }]
                            },
                            legend: {
                                display: true
                            },
                            elements: {
                                point: {
                                    radius: 3,
                                    backgroundColor: '#ff4c5b'
                                }
                            },
                            legendCallback: function (chart) {
                                var text = [];
                                text.push('<div class="item mr-4 d-flex align-items-center small">');
                                text.push(
                                    '<div class="item-box mr-2" data-color="' +
                                    chart.data.datasets[0].backgroundColor +
                                    ' "></div><p class="text-black mb-0"> ' +
                                    chart.data.datasets[0].label +
                                    "</p>"
                                );
                                text.push('</div>');
                                text.push('<div class="item d-flex align-items-center small">');
                                text.push(
                                    '<div class="item-box mr-2" data-color="' +
                                    chart.data.datasets[1].backgroundColor +
                                    '"></div><p class="text-black mb-0"> ' +
                                    chart.data.datasets[1].label +
                                    " </p>"
                                );
                                text.push('</div>');
                                return text.join('');
                            }
                        },
                    });
                }
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