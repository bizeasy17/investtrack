$(function(){
    var csrftoken = Cookies.get('csrftoken');
    var userBaseEndpoint = '/user/';
    
    var refreshAccountList = function (id, accountProvider, accountType, accountBalance, accountCapital, accountTradeFee, accountValidSince, prepend) {
        var accId = $("#hiddenAccId").val();
        if (prepend) {
            $("#accountList").prepend(
                '<a href="#" id="' + id + '" class="list-group-item d-flex justify-content-between list-group-item-action lh-condensed">'
                + '<div>'
                + '<h6 class="my-0">' + accountProvider + accountName + '</h6>'
                + '<small class="text-muted">' + accountType + '</small>'
                + '</div>'
                + '<span class="text-muted">' + accountBalance + '</span>'
                + '<input type="hidden" id="accProvider' + id + '" value="' + accountProvider + '"/>'
                + '<input type="hidden" id="accValidSince' + id + '"value="' + accountValidSince + '"/>'
                + '<input type="hidden" id="accTradeFee' + id + '" value="' + accountTradeFee + '"/>'
                + '<input type="hidden" id="accCapital' + id + '" value="' + accountCapital + '"/>'
                + '</a>'
            )
        } else {
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



    $("#btnSave").click(function () {
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
            var capitalOld = parseInt($('#accCapital' + $("#hiddenAccId").val()).val());
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
                if ($("#hiddenAccId").val() == '') {
                    var prepend = true;
                }
                $("#hiddenAccId").val(data.id);
                refreshAccountList(data.id, accountProvider, accountType, accountBalance, accountCapital, tradeFee, accountValidSince, prepend);
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
    document.getElementById('btnSaveAndEdit').addEventListener('click', createOrUpdateTradeAccount, event, false);

});