$(function () {
    var saBaseEndpoint = '/siteadmin/';

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

    var isTradeOfftime = function (inputDatetime) {
        // var dateAndTime = inputDatetime.split(" ");
        var date = formatDate(inputDatetime, "-");
        var openTime = new Date(date + " 9:30:00");
        var closeTime = new Date(date + " 15:05:00");
        if (inputDatetime >= closeTime) {
            return true;
        }
        return false;
    }

    $("#executeStockSnapshot").click(function () {
        if (!isTradeOfftime(new Date()))
            return;
        var appliedPeriod = "d";
        $('#snapshotSpinner').removeClass('d-none');
        $(this).prop("disabled", true);
        $.ajax({
            url: saBaseEndpoint + "snapshot/manual/",
            method: "GET",
            dataType: "json",
            success: function (data) {
                if (data.code == 'ok') {
                    $("#snapshotStatus").html(data.message);
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                } else {
                    $("#snapshotStatus").html("<p>" + data.message + "</p>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                }
            },
            error: function () {
                $("#snapshotStatus").html("<p>An error has occurred</p>");
                $("#snapshotSpinner").addClass("d-none");
                $("#executeStockSnapshot").removeAttr("disabled");
            },
            statusCode: {
                403: function () {
                    $("#snapshotStatus").append("<span>403 forbidden</span>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                },
                404: function () {
                    $("#snapshotStatus").append("<span>404 page not found</span>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                },
                500: function () {
                    $("#snapshotStatus").append("<span>500 internal server error</span>");
                    $("#snapshotSpinner").addClass("d-none");
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

