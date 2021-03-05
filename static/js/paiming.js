$(function () {
    var paimingEndpoint = '/paiming/';
    var stockmarketEndpoint = '/stockmarket/';
    var homeEndpoint = '/';
    var indexList = "sh,sz,cyb,hs300"
    var freq = "D";
    var histPeriod = 3;
    var histType = "close";
    var tsCode = "603799.SH";
    var tsCodeNoSfx = "";
    var stockName = "";
    var market = "";
    var pctOnPeriodDates = "";
    var periodOnPctDates = "";

    var bstr;
    var sstr;

    var today = new Date();
    var startQ = "199001";
    var endQ = "202101";
    var startDate = "";
    var endDate = "";
    // var countYear = 3;

    var strategyCode = "";
    var strategyName = "";
    var updownPctPeriod = 80;
    var expdPctPeriod = "pct20_period";

    var closeChart = echarts.init(document.getElementById('closeChart'));

    var initParam = function () {
        expdPctPeriod = $('input:radio[name="pct_period"]:checked').val();
        updownPctPeriod = $('input:radio[name="period"]:checked').val();
        strategyCode = $('input:radio[name="bstrategy"]:checked').val();
        strategyName = $('input:radio[name="bstrategy"]:checked').next().text();

        startDate = formatDate(new Date(today.getTime() - (365 * histPeriod * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");

        // initBTestDates();
    }


    var renderChart = function () {
        renderCloseChart();
    }

    var renderCloseChart = function () {
        $.ajax({
            url: stockmarketEndpoint + "stock-hist/" + tsCode + "/" + freq + "/" + histType + "/" + histPeriod + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: data.label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    series: [
                        {
                            name: '收',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(25, 70, 131)'
                            },
                            data: data.close
                        }
                    ]
                };

                closeChart.setOption(option);
            }
        });
    }

    // 初始化图表
    initParam();
    renderChart();
});