$(function () {
    var stockmarketEndpoint = '/stockmarket/';
    var investorsEndpoint = '/investors/';
    var board = "all";
    var province = "0";
    var city = "0";
    var industry = "0";
    var pb = "0";
    var pe = "0";
    var ps = "0";
    var holdPct = "0";

    var prevIndFilter = undefined;
    var prevIndMoreFilter = undefined;

    var startIdx = 0;
    var endIdx = 25;
    var rowCount = 25;
    var currentIdx = 0;
    var prevStockPickTr = undefined;
    var totalRowCount = 0
    var prevPagination;

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
                value: item.stock_code,
                text: item.stock_code + " - " + item.stock_name,
                html: [
                    item.stock_code + " - " + item.stock_name + "[" + item.market + "], " + item.area + ", " + item.industry + ", " + item.list_date + "上市",
                ]
            };
        },
        events: {
            search: function (qry, callback) {
                // let's do a custom ajax call
                $.ajax(
                    stockmarketEndpoint + 'companies/' + $('#searchText').val() + "/?format=json",
                ).done(function (companies) {
                    callback(companies)
                });
            }
        }
    });

    $('#searchText').on('autocomplete.select', function (evt, item) {
        console.log('select');
        var tsCode = item.ts_code;
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

    var buildFilter = function (board, province, city, industry, pe, pb, ps, holdPct) {
        return board + "," + province + "," + city + "," + industry + "," + pe + "," + pb + "," + ps + "," + holdPct;
    }

    var showBasicFilter = function () {
        if (!$("#basicFilter").is(":visible")) {
            $("#basicFilter").removeClass("d-none");
            $("#basicFilter").slideDown();
        } else {
            $("#basicFilter").slideUp();
        }
    }

    var showCityFilter = function (province) {
        if (!$("#cityFilter").is(":visible")) {
            $("#cityFilter").removeClass("d-none");
            $("#cityFilter").slideDown();
        } else {
            if (province == "0")
                $("#cityFilter").slideUp();
        }
    }

    var cityChange = function () {
        // alert($(this).val());
        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        city = $(this).val();
        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);
    }

    var bindCityFilter = function (province) {
        $.ajax({
            url: stockmarketEndpoint + "province/" + province + "/cities/4/",
            success: function (data) {
                $("#cityFilter").empty();
                var cityInput =
                    '<div class="btn-group btn-group-sm btn-group-toggle" data-toggle="buttons">' +
                    '<label class="btn btn-light active">' +
                    '<input type="radio" name="city" autocomplete="off" value="0" checked/><span class="text-warning">全部</span>' +
                    '</label>';
                $(data).each(function (idx, obj) {
                    cityInput +=
                        '<label class="btn btn-light">' +
                        '<input type="radio" name="city" autocomplete="off" value="' + obj.name + '" />' + obj.name +
                        '</label>';
                })
                cityInput +=
                    '<label class="btn btn-light">' +
                    '<input type="radio" name="city" autocomplete="off" value="more" />更多' +
                    '</label>' +
                    '</div>'
                $("#cityFilter").append(cityInput);


            },
            complete: function (request, status) {
                var cities = document.getElementsByName('city');
                $(cities).each(function (idx, obj) {
                    $(obj).on('change', cityChange);
                });
            }
        });
    }

    var bindIndustryBasic = function (industry) {
        $.ajax({
            url: stockmarketEndpoint + "industries/" + industry + "/",
            success: function (data) {
                if (data.length > 0) {
                    $("#headIndustry").text("("+industry+") ");
                    $("[id='iqt.1pe']").text(" " + data[0].pe_low);
                    $("[id='iqt.5pe']").text(" " + data[0].pe_med);
                    $("[id='iqt.9pe']").text(" " + data[0].pe_high);
                    $("[id='iqt.1pb']").text(" " + data[0].pb_low);
                    $("[id='iqt.5pb']").text(" " + data[0].pb_med);
                    $("[id='iqt.9pb']").text(" " + data[0].pb_high);
                    $("[id='iqt.1ps']").text(" " + data[0].ps_low);
                    $("[id='iqt.5ps']").text(" " + data[0].ps_med);
                    $("[id='iqt.9ps']").text(" " + data[0].ps_high);
                }
            }
        });
    }

    var showFilterResult = function (filters, startIdx, endIdx) {
        $.ajax({
            url: investorsEndpoint + "xuangu/filters/" + filters + "/" + startIdx + "/" + endIdx + "/",
            success: function (data) {
                $("#resultTbody").empty();
                $("#message").removeClass("d-none");
                if (data.count == 0) {
                    // alert("no data");
                    $("#message").text("无查询结果.");
                } else {
                    $(data.results).each(function (idx, obj) {
                        var textColor = "text-danger";
                        var pe = "";
                        var pe_ttm = "";
                        if (parseFloat(obj.chg_pct) < 0) {
                            textColor = "text-success";
                        }
                        if (parseFloat(obj.pe) == 0) {
                            pe = "亏"
                        } else {
                            pe = math.format(parseFloat(obj.pe), 3);
                        }
                        if (parseFloat(obj.pe_ttm) == 0) {
                            pe_ttm = "亏"
                        } else {
                            pe_ttm = math.format(parseFloat(obj.pe_ttm), 3);
                        }
                        var stockCard =
                            '<tr>' +
                                '<td id="cd{{k}}"><a href="/?q=' + obj.ts_code + '" class="text-primary" target="_blank">' + obj.ts_code + '</a></td>' +
                                '<td id="nm{{k}}"><a href="/?q=' + obj.ts_code + '" class="text-primary" target="_blank">' + obj.stock_name + '</a></td>' +
                                '<td class="text-muted" id="pe{{k}}">' + obj.industry + '</td>' +

                                '<td class="' + textColor + '" id="p{{k}}"><span>' + math.format(parseFloat(obj.close), 3) + '</span></td>' +
                                '<td class="' + textColor + '" id="pct{{k}}"><span>' + math.format(parseFloat(obj.chg_pct), 3) + '%</span></td>' +
                                '<td class="text-muted" id="pe{{k}}"><span>PE (' + pe + ')</span></td>' +
                                '<td class="text-muted" id="pe{{k}}"><span>PE动 (' + pe_ttm + ')</span></td>' +
                                '<td class="text-muted" id="pb{{k}}"><span>PB (' + math.format(parseFloat(obj.pb), 3) + ')</span></td>' +
                                '<td class="text-muted" id="ps{{k}}"><span>PS (' + math.format(parseFloat(obj.ps), 3) + ')</span></td>' +
                                '<td class="text-muted" id="mv{{k}}"><span>市值 (' + math.format(parseFloat(obj.total_mv) / 10000, 4) + '亿元)</span></td>' +
                                '<td class="text-muted" id="top10{{k}}"><span>持仓 (' + math.format(parseFloat(obj.top10_hold_pct), 3) + '%)</span></td>' +

                                // '<td class="dropdown">' +
                                //     '<a href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-expanded="false">' +
                                //     '<i class="fa fa-circle text-muted small" aria-hidden="true" id="tl{{k}}"></i>' +
                                //     '</a>' +
                                //     '<div class="dropdown-menu" aria-labelledby="navbarDropdown">' +
                                //     '<a class="dropdown-item small" href="javascript:void(0)" id="tlmsg{{k}}">无消息</a>' +
                                //     '</div>' +
                                // '</td>' +
                            '</tr>';
                        $("#resultTbody").append(stockCard);
                    })
                    totalRowCount = data.count;
                    $("#message").text("共有" + totalRowCount + "条结果，当前" + (currentIdx+1).toString() + " - " + (currentIdx + rowCount).toString() + "条");
                }
            },
            404: function () {
                $("#resultTbody").empty();
                console.info("404 page not found");
            },
            500: function () {
                $("#resultTbody").empty();
                $("#message").removeClass("d-none");
                $("#message").text("500 internal server error");
                console.info("500 internal server error");
            },
            complete: function (request, status) {
                $("#spinner").addClass("d-none");
            }
        });
    }

    $('input:radio[name="board"]').change(function () {
        // alert($(this).val());
        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        board = $(this).val();
        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);
    });

    $('input:radio[name="area"]').change(function () {
        // alert($(this).val());
        province = $(this).val();

        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        if (province != "0") {
            bindCityFilter(province);
        } else {
            city = "0";
        }
        showCityFilter(province);

        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);
    });


    $('input:radio[name="industry"]').change(function () {
        // alert($(this).val());
        prevIndFilter = this;
        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        // if (industry == "0" || $(this).val() == "0") {
        //     showBasicFilter();
        // }
        industry = $(this).val();
        bindIndustryBasic($(this).val());

        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);

        $(prevIndMoreFilter).css("background-color", "#f8f9fa");
    });

    $("#moreIndustry").click(function () {
        if (!$("#ind-filter-ext").is(":visible")) {
            $("#ind-filter-ext").removeClass("d-none");
            $("#ind-filter-ext").slideDown();
        } else {
            $("#ind-filter-ext").slideUp();
        }
    });

    $(".industry-more").click(function () {

        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        // if (industry == "0" || $(this).val() == "0") {
        //     showBasicFilter();
        // }
        industry = $(this).text();
        bindIndustryBasic($(this).text());
        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);

        // $(prevIndFilter).parent().removeClass("active");
        // $(prevIndFilter).removeAttr("checked");
        $(prevIndFilter).parent().removeClass("focus");
        $(prevIndFilter).parent().removeClass("active");

        $(prevIndMoreFilter).css("background-color", "#f8f9fa");
        $(this).css("background-color", "#dae0e5");

        prevIndMoreFilter = this;
    });

    $('input:radio[name="pe"]').change(function () {
        // alert($(this).val());

        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        pe = $(this).val();

        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);
    });

    $('input:radio[name="pb"]').change(function () {
        // alert($(this).val());

        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        pb = $(this).val();

        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);
    });

    $('input:radio[name="ps"]').change(function () {
        // alert($(this).val());

        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        ps = $(this).val();

        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);
    });

    $('input:radio[name="top10_holder"]').change(function () {
        // alert($(this).val());

        $("#spinner").removeClass("d-none");
        $("#message").addClass("d-none");

        holdPct = $(this).val();

        filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
        showFilterResult(filter, startIdx, endIdx);
    });


    $(".pagination").on("click", ".page-item", function (event) {
        $("#spinner").removeClass("d-none");

        if ($(this).index() == 0) {
            // prev
            if (currentIdx == 0) return;
            else {
                currentIdx -= rowCount;
            }
            console.log(currentIdx);
        } else {
            // next
            if (currentIdx + rowCount + 1 > totalRowCount) {
                return;
            }
            currentIdx += rowCount;
            console.log(currentIdx);
        }

        prevPagination = $(this);
        showFilterResult(filter, currentIdx, currentIdx + rowCount);
    });


    filter = buildFilter(board, province, city, industry, pe, pb, ps, holdPct);
    showFilterResult(filter, currentIdx, endIdx);
});