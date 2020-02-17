$(function () {
    var investBaseEndpoint = '/invest/stocks/';

    $("#executeStockSnapshot").click(function () {
        var appliedPeriod = "d";
        $('#execSpinner').removeClass('d-none');
        $(this).prop("disabled", true);
        $.ajax({
            url: investBaseEndpoint + "exec-snapshot/" + appliedPeriod,
            method: "GET",
            dataType: "json",
            success: function (data) {
                $("#execStatus").html(data.info);
                $("#syncSpinner").addClass("d-none");
                $("#executeStockSnapshot").removeAttr("disabled");
            },
            error: function () {
                $("#execStatus").html("<p>An error has occurred</p>");
                $("#execSpinner").addClass("d-none");
                $("#executeStockSnapshot").removeAttr("disabled");
            },
            statusCode: {
                403: function () {
                    $("#execStatus").append("<span>403 forbidden</span>");
                    $("#execSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                },
                404: function () {
                    $("#testInfo").append("<span>404 page not found</span>");
                    $("#execSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                },
                500: function () {
                    $("#execStatus").append("<span>500 internal server error</span>");
                    $("#execSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                }
            }
        });
    });

    $("#syncCompanyInfo").click(function () {
        $('#syncSpinner').removeClass('d-none');
        $(this).prop("disabled", true);

        $.ajax({
            url: investBaseEndpoint + 'sync-company-list/',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                $('#syncStatus').html(data.success);
                $('#syncSpinner').addClass('d-none');
                $('#syncCompanyInfo').removeAttr('disabled');
            },
            error: function () {
                $('#syncStatus').html('<p>An error has occurred</p>');
                $('#syncSpinner').addClass('d-none');
                $('#syncCompanyInfo').removeAttr('disabled');
            },
            statusCode: {
                403: function () {
                    $("#syncStatus").append("<span>403 forbidden</span>");
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');

                },
                404: function () {
                    $("#syncStatus").append("<span>404 page not found</span>");
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');

                },
                500: function () {
                    $("#syncStatus").append(
                        "<span>500 internal server error</span>"
                    );
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');
                }
            }
        });
    });
});

