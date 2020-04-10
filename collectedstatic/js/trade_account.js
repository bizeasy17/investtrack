$(function(){
    var csrftoken = Cookies.get('csrftoken');
    var userBaseEndpoint = '/user/';
    var dt = new Date();
    
    if ($("#accountValidSince").length > 0) {
        var date = formatDate(dt, "-");
        $("#accountValidSince").val(date);
    }
    
    var refreshAccountList = function (id, accountProvider, accountType, accountBalance, accountCapital, accountTradeFee, accountValidSince, prepend, capitalChange) {
        // var accId = $("#hiddenAccId").val();
        if (prepend) {
            $("#accountList").prepend(
                '<div id="' + id + '" class="list-group-item d-flex justify-content-between list-group-item-action lh-condensed">'
                    + '<div>'
                        + '<h6 class="my-0">' + accountProvider + accountType + '</h6>'
                        + '<small class="text-muted">' + accountType + '</small>'
                        + '<a href="/user/account/'+ id + '/trade/sh/" class="small badge-info badge-pill">记录交易</a>'
                    + '</div>'
                    + '<span class="text-muted">' + accountBalance + '</span>'
                    + '<input type="hidden" id="accProvider' + id + '" value="' + accountProvider + '"/>'
                    + '<input type="hidden" id="accValidSince' + id + '"value="' + accountValidSince + '"/>'
                    + '<input type="hidden" id="accTradeFee' + id + '" value="' + accountTradeFee + '"/>'
                    + '<input type="hidden" id="accCapital' + id + '" value="' + accountCapital + '"/>'
                    + '<input type="hidden" id="accId' + id + '" value="' + id + '"/>'
                + '</div>'
            )
            $("#"+id).click(function () {
                // alert($(this).attr('id') + 'clicked');
                $('#accountProvider').val($("#accProvider" + $(this).attr('id')).val());
                $('#accountType').val($(this).find('small').text());
                $('#accountCapital').val($("#accCapital" + $(this).attr('id')).val());
                $('#accountBalance').val($(this).find('span').text());
                $('#tradeFee').val($("#accTradeFee" + $(this).attr('id')).val());
                $('#accountValidSince').val($("#accValidSince" + $(this).attr('id')).val());
                $("#hiddenAccId").val($(this).attr('id'));
            });
        } else { 
            // 更新已经在列表指定ID的trade account
            $("#" + id).find('h6').text(accountProvider + accountType);
            $("#" + id).find('small').text(accountType);
            $("#" + id).find('span').text(accountBalance);
            $("#accCapital" + id).val(accountCapital);
            $("#accTradeFee" + id).val(accountTradeFee);
            $("#accValidSince" + id).val(accountValidSince);
            $("#accProvider" + id).val(accountProvider);
        }
        if (parseFloat($("#totalAccBalance").text())==0){
            $("#totalAccBalance").text(accountCapital)
        }else{
            $("#totalAccBalance").text(parseFloat($("#totalAccBalance").text()) + parseFloat(capitalChange));
        }
    }
    // y用户管理
    $('input[type = file]').change(function () {
        //get the file name
        var fileName = $(this).val();
        //replace the "Choose a file" label
        $(this).next('.custom-file-label').html(fileName);
    });

    

    // var capitalNew;
    $(".list-group-item").click(function () {
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

    var bindTradeAccountList = function(){
        $.ajax({
            url: userBaseEndpoint + 'trade-accounts/',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                $(data).each(function(idx, obj){

                });
            }
        });
    }

    var removeTradeAccount = function (event) {
        event.preventDefault();
        $.ajax({
            url: userBaseEndpoint + 'account/remove',
            method: 'POST',
            dataType: 'json',
            success: function (data) {
                $(data).each(function (idx, obj) {

                });
            }
        });
    }

    var createOrUpdateTradeAccount = function (event, continueEdit) {
        event.preventDefault();
        var accountBalance = $('#accountBalance').val();
        var accountProvider = $('#accountProvider').val();
        var accountType = $('#accountType').val();
        var accountCapital = $('#accountCapital').val();
        var tradeFee = $('#tradeFee').val();
        var accountValidSince = $('#accountValidSince').val();
        var capitalChange = 0;

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
            capitalChange = $('#accountCapital').val();
        } else {
            var capitalOld = parseFloat($('#accCapital' + $("#hiddenAccId").val()).val());
            var capitalNew = parseFloat($('#accountCapital').val());
            capitalChange = capitalNew - capitalOld;
            // $('#accountBalance').val("is-invalid");
            accountBalance = parseFloat(accountBalance) + capitalChange;
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
                if ($("#hiddenAccId").val() == '') {
                    var prepend = true;
                }
                // $("#accId").val(data.id);
                refreshAccountList(data.id, accountProvider, accountType, accountBalance, accountCapital, tradeFee, accountValidSince, prepend, capitalChange);
                if (continueEdit) {
                    // 保持，并继续编辑
                } else {
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
    document.getElementById('btnSaveAndEdit').addEventListener('click', createOrUpdateTradeAccount, event, true);
    document.getElementById('btnRemove').addEventListener('click', removeTradeAccount, event);

});