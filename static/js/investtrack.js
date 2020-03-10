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
