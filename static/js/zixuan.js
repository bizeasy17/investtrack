$(function () {
    var stockmarketEndpoint = '/stockmarket/';
    var zixuanEndpoint = '/zixuan/';
    var indexList = "sh,sz,cyb,hs300"

    $(window).keydown(function (event) {
        if ((event.keyCode == 13) && ($("#searchText").val() == "")) {
            event.preventDefault();
            return false;
        }
    });

    $('#searchText').autoComplete({
        resolver: 'custom',
        // preventEnter: true,
        formatResult: function (item) {
            return {
                value: item.id,
                text: item.id + " - " + item.text,
                html: [
                    item.id + " - " + item.text + " [" + item.market + "], " + item.area + ", " + item.industry + ", " + item.list_date + "上市",
                ]
            };
        },
        events: {
            search: function (qry, callback) {
                // let's do a custom ajax call
                $.ajax(
                    stockmarketEndpoint + 'companies/' + $('#searchText').val(),
                ).done(function (res) {
                    callback(res.results)
                });
            }
        }
    });

    $('#searchText').on('autocomplete.select', function (evt, item) {
        console.log('select');
        var stockCode = item.id;
        var tsCode = item.ts_code;
        var stockName = item.text;
        var market = item.market;
        $("#searchText").val(tsCode);
        $("#searchForm").submit();
        // var curUrl = window.document.location.href;
        // var PERFIX;
        // PERFIX = curUrl.substring(0, curUrl.indexOf("web"));
        // window.location.replace(location.protocol + "//" + location.host + "/?q=" + tsCode);

        // $.ajax({
        //     url: zixuanEndpoint + 'selected-stk-price/',
        //     success: function (data) {

        //     }
        // });
    });

    var showSelectedPrice = function () {
        $.ajax({
            url: zixuanEndpoint + 'selected-stk-price/',
            success: function (data) {
                // $(data.content).each(function (idx, obj) {
                //     // alert(idx);
                //     $("#p" + idx).text(obj[0]);
                //     $("#pct" + idx).text(obj[1]+"%");
                // });
                var content = data.content;
                for (var key in content) {
                    $("[id='p" + key + "']").text(content[key][0]);     //获取key值
                    $("[id='pct" + key + "']").text(content[key][1] + "%");
                    if (parseFloat(content[key][1]) >= 0) {
                        $("[id='p" + key + "']").removeClass("text-muted");
                        $("[id='pct" + key + "']").removeClass("text-muted");
                        $("[id='p" + key + "']").addClass("text-danger");
                        $("[id='pct" + key + "']").addClass("text-danger");
                    } else {
                        $("[id='p" + key + "']").removeClass("text-muted");
                        $("[id='pct" + key + "']").removeClass("text-muted");
                        $("[id='p" + key + "']").addClass("text-success");
                        $("[id='pct" + key + "']").addClass("text-success");
                    }

                    showSelectedTraffic(key);
                    // if (content[key][4] != undefined && content[key][4].length > 0 && content[key][4][0].hasOwnProperty("traffic_light")) {
                    //     if (content[key][4][0].traffic_light == "G") {
                    //         $("[id='tl" + key + "']").removeClass("text-muted");
                    //         $("[id='tl" + key + "']").addClass("text-success");
                    //         $("[id='tlmsg" + key + "']").text(content[key][4][0].msg);
                    //     }

                    //     if (content[key][4][0].traffic_light == "Y") {
                    //         $("[id='tl" + key + "']").removeClass("text-muted");
                    //         $("[id='tl" + key + "']").addClass("text-warning");
                    //         $("[id='tlmsg" + key + "']").text(content[key][4][0].msg);
                    //     }

                    //     if (content[key][4][0].traffic_light == "R") {
                    //         $("[id='tl" + key + "']").removeClass("text-muted");
                    //         $("[id='tl" + key + "']").addClass("text-danger");
                    //         $("[id='tlmsg" + key + "']").text(content[key][4][0].msg);
                    //     }
                    // }
                }
            }
        });
    }

    var showSelectedTraffic = function (tsCode) {
        $.ajax({
            url: zixuanEndpoint + 'selected-stk-traffic/' + tsCode + "/",
            success: function (data) {
                // $(data.content).each(function (idx, obj) {
                //     // alert(idx);
                //     $("#p" + idx).text(obj[0]);
                //     $("#pct" + idx).text(obj[1]+"%");
                // });
                var content = data.content;
                for (var key in content) {
                    // $("[id='pct" + key + "'").append("<span class='badge badge-pill badge-danger'>9</span>");
                    if (content[key] != undefined && content[key].hasOwnProperty("traffic_light")) {
                        if (content[key].traffic_light == "G") {
                            $("[id='tl" + content[key].ts_code + "']").removeClass("text-muted");
                            $("[id='tl" + content[key].ts_code + "']").addClass("text-success");
                            $("[id='tlmsg" + content[key].ts_code + "']").text(content[key].msg);
                        }

                        if (content[key].traffic_light == "Y") {
                            $("[id='tl" + content[key].ts_code + "']").removeClass("text-muted");
                            $("[id='tl" + content[key].ts_code + "']").addClass("text-warning");
                            $("[id='tlmsg" + content[key].ts_code + "']").text(content[key].msg);
                        }

                        if (content[key].traffic_light == "R") {
                            $("[id='tl" + content[key].ts_code + "']").removeClass("text-muted");
                            $("[id='tl" + content[key].ts_code + "']").addClass("text-danger");
                            $("[id='tlmsg" + content[key].ts_code + "']").text(content[key].msg);
                        }
                    }
                }
            }
        });
    }

    // $(".navbar-toggler").click(function(){
    //     if($(this).next().is(":visible")){
    //         $(this).next().slideUp();
    //     }else{
    //         $(this).next().slideDown();
    //     }
    // });

    showSelectedPrice();
});