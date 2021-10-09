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
                    if (content[key][4] != undefined) {
                        if (content[key][4]!="0"){
                            $("[id='pe" + key + "']").text("市盈(" + content[key][4] + ")");
                            $("[id='pe" + key + "']").addClass("text-primary");
                        }else{
                            $("[id='pe" + key + "']").text("市盈(亏)");
                            $("[id='pe" + key + "']").addClass("text-primary");
                        }
                    }
                    else {
                        $("[id='pe" + key + "']").text("市盈(无)");
                        $("[id='pe" + key + "']").addClass("text-primary");
                    }

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
            },
            complete: function(request, status){
                $("#spinner").addClass("d-none");
            }
        });
    }

    var showIndBasic = function () {
        var basicType = "pe";
        var indContainer = $(".industry");
        $(indContainer).each(function (idx, obj) {
            $.ajax({
                url: stockmarketEndpoint + "industry-latest-daily-basic/" + $(obj).attr("name") + "/" + basicType + "/",
                success: function (data) {
                    // $(data.content).each(function (idx, obj) {
                    //     // alert(idx);
                    //     $("#p" + idx).text(obj[0]);
                    //     $("#pct" + idx).text(obj[1]+"%");
                    // });
                    var content = data.content;
                    for (var key in content) {
                        // $("[id='pct" + key + "'").append("<span class='badge badge-pill badge-danger'>9</span>");
                        $(content[key]).each(function(id, ob){
                            if (ob.qt == "0.1") {
                                $("[id='qt.1" + key + "']").text(" " + ob.val);
                            }

                            if (ob.qt == "0.5") {
                                $("[id='qt.5" + key + "']").text(" " + ob.val);
                            }

                            if (ob.qt == "0.9") {
                                $("[id='qt.9" + key + "']").text(" " + ob.val);
                            }
                        });
                        // if (content[key] != undefined && content[key].hasOwnProperty("qt")) {
                            
                        // }
                    }
                }
            });
            if (obj.code == "000001") {
                index = "sh";
            } else if (obj.code){

            }
        });
        
    }

    var showIndustries = function(){
        $.ajax({
            url: stockmarketEndpoint + "industries/" + $("#myIndustries").val() + "/",
            success: function (data) {

                $(data).each(function (idx, obj) {
                    var stockCard = 
                            '<div class="mt-3 col-md-4 stretch-card">'+
                                '<div class="card">' +
                                    '<div class="card-body">' +
                                        '<div class="d-flex align-items-center justify-content-between flex-wrap">'+
                                            '<div class="card-title"><a class="text-muted" href="javascript:void(0);"><h6>'+obj.industry+'</h6></a></div>'+
                                            '<p class="font-weight-medium small">'+
                                                '<span class="badge badge-primary rounded-pill">'+obj.stock_count+'</span>'+
                                            '</p>'+
                                        '</div>'+
                                        '<div class="container small col-lg-12 industry">'+
                                            '<span class="text-muted" >行业市盈率:</span>'+
                                            '<span class="text-success"><i class="fa fa-circle small" aria-hidden="true"></i> '+obj.pe_low+'</span>'+
                                            '<span class="text-warning ml-1"><i class="fa fa-circle small" aria-hidden="true"></i> ' + obj.pe_med +'</span>'+
                                            '<span class="text-danger ml-1"><i class="fa fa-circle small" aria-hidden="true"></i> ' + obj.pe_high+'</span>'+
                                        '</div>'+
                                        '<div class="container small mt-3">';
                    $.ajax({
                        url: zixuanEndpoint + "industries/" + obj.industry + "/my-company-daily-basic/",
                        success: function (cdb) {
                            $(cdb).each(function(id, ob){
                                var highColor = "danger";
                                if(parseFloat(ob.chg_pct)<0){
                                    highColor = "success";
                                }
                                stockCard +=    '<div class="d-flex align-items-left justify-content-between flex-wrap row mt-1">'+
                                                    '<div><a href="/?q='+ob.ts_code+'" class="text-primary" target="_blank">'+ob.ts_code+'</a></div>'+
                                                    '<span><a href="/?q='+ob.ts_code+'" class="text-primary" target="_blank">'+ob.stock_name+'</a></span>'+
                                                    '<span class="text-'+highColor+'">'+ob.close+'</span>'+
                                                    '<span class="text-'+highColor+'">'+ob.chg_pct+'</span>'+
                                                    '<span class="text-primary">' + ob.pe +'(PE)</span>'+
                                                    '<div class="dropdown">'+
                                                        '<a href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-expanded="false">'+
                                                            '<i class="fa fa-circle text-muted small" aria-hidden="true" id="tl{{k}}"></i>'+
                                                        '</a>'+
                                                        '<div class="dropdown-menu" aria-labelledby="navbarDropdown">'+
                                                            '<a class="dropdown-item small" href="javascript:void(0)" id="tlmsg{{k}}">无消息</a>'+
                                                        '</div>'+
                                                    '</div>'+
                                                '</div>';
                            });
                        },
                        complete: function(request, status){
                            stockCard += '</div>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>';
                            
                            $("#spinner").addClass("d-none");
                            $("#companiesByIndustryContainer").append(stockCard);
                        }
                    });
                });
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

    showIndBasic();
    showSelectedPrice();
    // showIndustries();
});