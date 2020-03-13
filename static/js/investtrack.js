/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

function formatDate(date, conn) {
    var dayNames = [
        "01", "02", "03",
        "04", "05", "06", "07",
        "08", "09", "10",
        "11", "12", "13", "14",
        "15", "16", "17", "18",
        "19", "20", "21", "22",
        "23", "24", "25", "26",
        "27", "28", "29", "30", "31"
    ];

    var monthNames = [
        "01", "02", "03",
        "04", "05", "06", "07",
        "08", "09", "10",
        "11", "12"
    ];

    var dayIndex = date.getDate();
    var monthIndex = date.getMonth();
    var year = date.getFullYear();

    return year + conn + monthNames[monthIndex] + conn + dayNames[dayIndex - 1];
}

/* Notifications JS basic client */
$(function () {
    var csrftoken = Cookies.get('csrftoken');
    var userBaseEndpoint = '/user/';
    let emptyMessage = '你有新的通知';
    function checkNotifications() {
        $.ajax({
            url: '/notifications/latest-notifications/',
            cache: false,
            success: function (data) {
                if (!data.includes(emptyMessage)) {
                    $("#notifications").addClass("btn-danger");
                }
            },
        });
    };

    function update_social_activity (id_value) {
        let newsToUpdate = $("[news-id=" + id_value + "]");
        payload = {
            'id_value': id_value,
        };
        $.ajax({
            url: '/news/update-interactions/',
            data: payload,
            type: 'POST',
            cache: false,
            success: function (data) {
                $(".like-count", newsToUpdate).text(data.likes);
                $(".comment-count", newsToUpdate).text(data.comments);
            },
        });
    };

    checkNotifications();

    $('#notifications').popover({
        html: true,
        trigger: 'manual',
        container: "body" ,
        placement: "bottom",
    });

    $("#notifications").click(function () {
        if ($(".popover").is(":visible")) {
            $("#notifications").popover('hide');
            checkNotifications();
        }
        else {
            $("#notifications").popover('dispose');
            $.ajax({
                url: '/notifications/latest-notifications/',
                cache: false,
                success: function (data) {
                    $("#notifications").popover({
                        html: true,
                        trigger: 'focus',
                        container: "body" ,
                        placement: "bottom",
                        content: data,
                    });
                    $("#notifications").popover('show');
                    $("#notifications").removeClass("btn-danger")
                },
            });
        }
        return false;
    });

    // Code block to manage WebSocket connections
    // Try to correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/notifications/";
    let webSocket = new channels.WebSocketBridge();
    webSocket.connect(ws_path);

    // Helpful debugging
    webSocket.socket.onopen = function () {
        console.log("Connected to " + ws_path);
    };

    webSocket.socket.onclose = function () {
        console.error("Disconnected from " + ws_path);
    };

    // Listen the WebSocket bridge created throug django-channels library.
    webSocket.listen(function(event) {
        switch (event.key) {
            case "notification":
                $("#notifications").addClass("btn-danger");
                break;

            case "social_update":
                $("#notifications").addClass("btn-danger");
                update_social_activity(event.id_value);
                break;

            case "additional_news":
                if (event.actor_name !== currentUser) {
                    $(".stream-update").show();
                }
                break;

            default:
                console.log('error: ', event);
                break;
        };
    });

    // 业务相关代码
    var chart;

    var csrftoken = Cookies.get('csrftoken');
    var userBaseEndpoint = '/user/';
    var investBaseEndpoint = '/invest/stocks/';

    var chartShowDays15 = 5
    var chartShowDays30 = 10
    var chartShowDays60 = 15
    var chartShowDays = 60
    var chartShowDaysW = 180
    var chartShowDaysM = 720

    var dt = new Date();
    var endDate = formatDate(dt, '-');
    var chartCanvas = document.getElementById('bsChart').getContext('2d');

    // 更新当前所选股票信息
    var updateChart = function () {
        var dataset = chart.config.data.datasets[0];
        chart.update();
    };

    var getStartDate = function (period, format) {
        var priorDate;
        if (period == '15')
            priorDate = new Date(dt.getTime() - (chartShowDays15 * 24 * 60 * 60 * 1000));
        else if (period == '30')
            priorDate = new Date(dt.getTime() - (chartShowDays30 * 24 * 60 * 60 * 1000));
        else if (period == '60')
            priorDate = new Date(dt.getTime() - (chartShowDays60 * 24 * 60 * 60 * 1000));
        else if (period == 'D')
            priorDate = new Date(dt.getTime() - (chartShowDays * 24 * 60 * 60 * 1000));
        else if (period == 'W')
            priorDate = new Date(dt.getTime() - (chartShowDaysW * 24 * 60 * 60 * 1000));
        else if (period == 'M')
            priorDate = new Date(dt.getTime() - (chartShowDaysM * 24 * 60 * 60 * 1000));

        return formatDate(priorDate, format);
    }

    var updateChartFor = function (showName, showCode, tsCode, period) {
        var startDate = getStartDate(period, '-');

        $.ajax({
            url: investBaseEndpoint + 'get-price/' + tsCode + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                $("#spBsChart").addClass("d-none");//隐藏spinner
                chart.data.datasets.forEach(function (dataset) {
                    dataset.data = data;
                    dataset.label = showName + ' - ' + showCode;
                });
                updateChart();
            }
        })
    }

    // 页面默认加载上证指数日K（D)
    var initStockChart = function (code, showCode, showName) {
        var period = $('input:radio[name="period"]:checked').val();
        var startDate = getStartDate(period, '-');
        // var code = $('input:radio[name="index"]:checked').val(); // e.g. sh
        // var showCode = $('input:radio[name="index"]:checked').attr('id')// e.g. 1A0001 上证
        // var showName = $('input:radio[name="index"]:checked').parent().text().trim();

        $.ajax({
            url: investBaseEndpoint + 'get-price/' + code + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                // ctx1.canvas.width = 1000;
                // ctx1.canvas.height = 250;
                $("#spBsChart").addClass("d-none");//隐藏spinner
                chart = new Chart(chartCanvas, {
                    type: 'candlestick',
                    data: {
                        datasets: [{
                            label: showName + '-' + showCode,
                            data: data
                        }]
                    },
                    options: {
                        scales: {
                            xAxes: [{
                                afterBuildTicks: function (scale, ticks) {
                                    var majorUnit = scale._majorUnit;
                                    var firstTick = ticks[0];
                                    var i, ilen, val, tick, currMajor, lastMajor;

                                    val = luxon.DateTime.fromMillis(ticks[0].value);
                                    if ((majorUnit === 'minute' && val.second === 0)
                                        || (majorUnit === 'hour' && val.minute === 0)
                                        || (majorUnit === 'day' && val.hour === 9)
                                        || (majorUnit === 'month' && val.day <= 3 && val.weekday === 1)
                                        || (majorUnit === 'year' && val.month === 0)) {
                                        firstTick.major = true;
                                    } else {
                                        firstTick.major = false;
                                    }
                                    lastMajor = val.get(majorUnit);

                                    for (i = 1, ilen = ticks.length; i < ilen; i++) {
                                        tick = ticks[i];
                                        val = luxon.DateTime.fromMillis(tick.value);
                                        currMajor = val.get(majorUnit);
                                        tick.major = currMajor !== lastMajor;
                                        lastMajor = currMajor;
                                    }
                                    return ticks;
                                }
                            }]
                        }
                    }
                });
            }
        });
    }

    initStockChart($('#hiddenCode').val(), $('#hiddenTscode').val(), $('#hiddenName').val());


    $('input:radio[name="period"]').change(function () {
        // 设置当前选定股票
        var code = $('#hiddenCode').val()
        var showCode = $('#hiddenTscode').val();
        var showName = $('#hiddenName').val();
        var period = $(this).val();
        updateChartFor(showName, showCode, code, period);
    });

    $("#collapseChart").click(function(){
        if ($("#chartContainer").hasClass("collapse")){
            $("#chartContainer").removeClass("collapse");
            $(this).val("收起k线图");
        }else{
            $("#chartContainer").addClass("collapse");
            $(this).val("展开k线图");

        }
    });

    var refreshAccountList = function (id, accountProvider, accountType, accountBalance, accountCapital, accountTradeFee, accountValidSince, prepend){
        var accId = $("#hiddenAccId").val();
        if (prepend){
            $("#accountList").prepend(
                '<a href="#" id="'+id+'" class="list-group-item d-flex justify-content-between list-group-item-action lh-condensed">'
                    + '<div>'
                    + '<h6 class="my-0">' +accountProvider + accountName+'</h6>'
                        + '<small class="text-muted">'+accountType+'</small>'
                    + '</div>'
                    + '<span class="text-muted">'+accountBalance+'</span>'
                    + '<input type="hidden" id="accProvider'+id+'" value="' + accountProvider + '"/>'
                    + '<input type="hidden" id="accValidSince' + id + '"value="' + accountValidSince + '"/>'
                    + '<input type="hidden" id="accTradeFee' + id + '" value="' + accountTradeFee + '"/>'
                    + '<input type="hidden" id="accCapital' + id + '" value="' + accountCapital + '"/>'
                + '</a>'
            )
        }else{
            $("#" + accId).find('h6').text(accountProvider + accountType);
            $("#" + accId).find('small').text(accountType);
            $("#" + accId).find('span').text(accountBalance);
            $("#accCapital" + accId).val(accountCapital);
            $("#accTradeFee" + accId).val(accountTradeFee);
            $("#accValidSince" + accId).val(accountValidSince);
            $("#accProvider" + accId).val(accountProvider);
        }
        $("#totalAccBalance").text((parseInt($("#totalAccBalance").text()) + parseInt(accountBalance)).toLocaleString());
    }
    // y用户管理
    $('input[type = file]').change(function () {
        //get the file name
        var fileName = $(this).val();
        //replace the "Choose a file" label
        $(this).next('.custom-file-label').html(fileName);
    });

    // 显示s相关操作
    $('input[name = sRelatedTrade]').click(function () {
        //get the file name
        var id = $(this).attr("id");
        //replace the "Choose a file" label
        alert(id);
    });

    // 显示b相关操作
    $('input[name = bRelatedTrade]').click(function () {
        //get the file name
        var id = $(this).attr("id");
        //replace the "Choose a file" label
        alert(id);
    });

    $("#btnSave").click(function(){
        event.preventDefault();
        var name = $('#name').val();
        var email = $('#email').val();
        var jobTitle = $('#jobTitle').val();
        var location = $('#location').val();
        var shortBio = $('#shortBio').val();
        var portrait = $('#filePortrait').val()

        if (name.length < 1) {
            $('#name').addClass("is-invalid");
            return;
        } else {
            $('#name').removeClass("is-invalid");
        }

        if (email.length < 1) {
            $('#email').addClass("is-invalid");
            return;
        } else {
            $('#email').removeClass("is-invalid");
        }

        var form = $("#userForm");
        var formData = new FormData(form[0]);

        $.ajax({
            url: userBaseEndpoint + 'profile/update',
            enctype: 'multipart/form-data',
            headers: { 'X-CSRFToken': csrftoken },
            method: 'POST',
            processData: false,
            contentType: false,
            // dataType: 'json',
            data: formData,
            // {
                // name: name,
                // email: email,
                // jobTitle: jobTitle,
                // location: location,
                // shortBio: shortBio,
                // portrait: portrait,
            // },
            success: function (data) {
                $("#messages").removeClass('d-none');
                $('#messages').removeClass('alert-warning');
                $("#messages").addClass('alert-success');
                $("#messageText").html('<strong>' + data.message + '</strong>.');
            },
            statusCode: {
                403: function () {
                    $("#messages").removeClass('d-none');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>403 forbidden</strong>.');
                },
                404: function () {
                    $("#messages").removeClass('d-none');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>404 page not found</strong>.');
                },
                500: function () {
                    $("#messages").removeClass('d-none');
                    $('#messages').removeClass('alert-success');
                    $('#messages').addClass('alert-warning');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>500 internal server error</strong>.');
                }
            }
        });
    });

    $('.close').click(function () {
        // e.preventDefault();
        $('#messages').addClass('d-none');
    });
    // var capitalNew;
    $("#accountList").find('a').click(function(){
        // alert($(this).attr('id') + 'clicked');
        $('#accountProvider').val($("#accProvider" + $(this).attr('id')).val());
        $('#accountType').val($(this).find('small').text());
        $('#accountCapital').val($("#accCapital" + $(this).attr('id')).val());
        $('#accountBalance').val($(this).find('span').text());
        $('#tradeFee').val($("#accTradeFee" + $(this).attr('id')).val());
        $('#accountValidSince').val($("#accValidSince" + $(this).attr('id')).val());
        $("#hiddenAccId").val($(this).attr('id'));
    });

    // $('#accountCapital').blur(function () {
    //     capitalNew = $(this).val();
    // });

    var createOrUpdateTradeAccount = function (event, continueEdit) {
        event.preventDefault();
        var accountBalance = $('#accountBalance').val();
        var accountProvider = $('#accountProvider').val();
        var accountType = $('#accountType').val();
        var accountCapital = $('#accountCapital').val();
        var tradeFee = $('#tradeFee').val();
        var accountValidSince = $('#accountValidSince').val();

        if (accountProvider.length < 1) {
            $('#accountProvider').addClass("is-invalid");
            return;
        } else {
            $('#accountProvider').removeClass("is-invalid");
        }

        if (accountType.length < 1) {
            $('#accountType').addClass("is-invalid");
            return;
        } else {
            $('#accountType').removeClass("is-invalid");
        }

        if (accountCapital.length < 1) {
            $('#accountCapital').addClass("is-invalid");
            return;
        } else {
            $('#accountCapital').removeClass("is-invalid");
        }

        if (accountBalance.length < 1) {
            accountBalance = $('#accountCapital').val();
            return;
        } else {
            var capitalOld = parseInt($('#accCapital'+ $("#hiddenAccId").val()).val());
            var capitalNew = parseInt($('#accountCapital').val());
            // $('#accountBalance').val("is-invalid");
            accountBalance = parseInt(accountBalance) + (capitalNew - capitalOld);
        }

        if (tradeFee.length < 1) {
            $('#tradeFee').addClass("is-invalid");
            return;
        } else {
            $('#tradeFee').removeClass("is-invalid");
        }

        if (accountValidSince.length < 1) {
            $('#accountValidSince').addClass("is-invalid");
            return;
        } else {
            $('#accountValidSince').removeClass("is-invalid");
        }

        $.ajax({
            url: userBaseEndpoint + 'create-account',
            headers: { 'X-CSRFToken': csrftoken },
            method: 'POST',
            dataType: 'json',
            data: {
                accountId: $("#hiddenAccId").val(),
                accountProvider: accountProvider,
                accountType: accountType,
                accountCapital: accountCapital,
                accountBalance: accountBalance,
                tradeFee: tradeFee,
                accountValidSince: accountValidSince,
            },
            success: function (data) {
                $("#messages").removeClass('d-none');
                $('#messages').removeClass('alert-warning');
                $("#messages").addClass('alert-success');
                $("#messageText").html('<strong>' + data.message + '</strong>.');
                // $("#messages").fadeOut(2000);
                var prepend = false;
                if($("#hiddenAccId").val()==''){
                    var prepend = true;
                }
                $("#hiddenAccId").val(data.id);
                refreshAccountList(data.id, accountProvider, accountType, accountBalance, accountCapital, tradeFee, accountValidSince, prepend);
                if (continueEdit){
                    // 保持，并继续编辑
                }else{
                    // 清空field
                    $("#hiddenAccId").val('');
                    $('#accountProvider').val('');
                    $('#accountType').val('');
                    $('#accountCapital').val('');
                    $('#accountBalance').val('');
                    $('#tradeFee').val('');
                    $('#accountValidSince').val('');
                }
            },
            statusCode: {
                403: function () {
                    $("#messages").removeClass('d-none');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>403 forbidden</strong>.');
                },
                404: function () {
                    $("#messages").removeClass('d-none');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>404 page not found</strong>.');
                },
                500: function () {
                    $("#messages").removeClass('d-none');
                    $('#messages').removeClass('alert-success');
                    $('#messages').addClass('alert-warning');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>500 internal server error</strong>.');
                }
            }
        });
    }

    // $('#btnSaveTradeAccount').click(createOrUpdateTradeAccount(event, false)); 
    // $('#btnSaveAndEdit').click(createOrUpdateTradeAccount(event, true));
    // 创建完后，清空。可以创建下一个
    document.getElementById('btnSaveTradeAccount').addEventListener('click', createOrUpdateTradeAccount, event, false);
    // 创建完后，不清空。可以继续编辑
    document.getElementById('btnSaveAndEdit').addEventListener('click', createOrUpdateTradeAccount, event, false);
    
});
