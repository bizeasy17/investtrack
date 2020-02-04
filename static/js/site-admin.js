$(function () {
    var investBaseEndpoint = '/invest/stocks/';

    $("#syncCompanyInfo").click(function(){
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
                    $('#testInfo').append('<span>403 forbidden</span>');
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');

                },
                404: function () {
                    $('#testInfo').append('<span>404 page not found</span>');
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');

                },
                500: function () {
                    $('#testInfo').append('<span>500 internal server error</span>');
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');
                }
            }
        });
    });
});

