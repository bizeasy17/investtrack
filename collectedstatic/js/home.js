$(function () {
    var chart;
    var userBaseEndpoint = '/user/';
    var investBaseEndpoint = '/invest/stocks/';
    var indexList = "sh,sz,cyb"
    $.ajax({
        url: investBaseEndpoint + 'get-realtime-quotes/' + indexList + '/',
        success: function (data) {
            var index = "sh"
            $(data).each(function(idx, obj){
                // alert(idx);
                if(obj.code=="000001"){
                    index = "sh";
                }else if(obj.code=="399001"){
                    index = "sz";
                }else{
                    index = "cyb";
                }
                var change = Math.round((parseFloat(obj.price) - parseFloat(obj.pre_close)) / parseFloat(obj.pre_close) * 10000)/100;
                if(change >= 0){
                    $("#" + index + "Change").removeClass("text-success");
                    $("#" + index + "Change").addClass("text-danger");
                    $("#" + index + "Price").removeClass("text-success");
                    $("#" + index + "Price").addClass("text-success");
                }else{
                    $("#" + index + "Change").addClass("text-success");
                    $("#" + index + "Change").removeClass("text-danger");
                    $("#" + index + "Price").addClass("text-success");
                    $("#" + index + "Price").removeClass("text-danger");
                }
                change = change + "%";
                $("#" + index + "Change").text(change);
                $("#" + index + "Price").text(obj.price);
                $("#" + index + "PreClose").text(obj.pre_close);
                $("#" + index + "Amount").text((Math.round(parseInt(obj.amount)/100000000)).toLocaleString());
                $("#" + index + "Volume").text((parseInt(obj.volume/1000000)).toLocaleString());
            });
        }
    });

});