var chartShowDays60 = 60;
var chartShowDays = 60;
var chartShowDaysW = 180;
var chartShowDaysM = 720;

var closeChartShowDays = 365 * 2;

var formatDate = function (date, connector) {
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

    return year + connector + monthNames[monthIndex] + connector + dayNames[dayIndex - 1];
}

var isOpenForTrade = function (inputDatetime) {
    // var dateAndTime = inputDatetime.split(" ");
    var date = formatDate(inputDatetime, "-");
    var openTime = new Date(date + " 9:30:00");
    var morningCloseTime = new Date(date + " 11:30:00");
    var afternoonOpenTime = new Date(date + " 13:00:00");
    var closeTime = new Date(date + " 15:05:00");
    var day = inputDatetime.getDay();
    var hour = inputDatetime.getHours();
    var min = inputDatetime.getMinutes();
    if (day == 0 || day == 6) return false; //周六周日不需要刷新
    if (inputDatetime >= openTime && inputDatetime <= morningCloseTime) {
        return true;
    }
    if (inputDatetime >= afternoonOpenTime && inputDatetime <= closeTime) {
        return true;
    }
    if (inputDatetime > date) {
        return false;
    }
    return false;
}

var getStartDate = function (period, format) {
    var dt = new Date();
    var priorDate;
    if (period == '60')
        priorDate = new Date(dt.getTime() - (chartShowDays60 * 24 * 60 * 60 * 1000));
    else if (period == 'D')
        priorDate = new Date(dt.getTime() - (chartShowDays * 24 * 60 * 60 * 1000));
    else if (period == 'W')
        priorDate = new Date(dt.getTime() - (chartShowDaysW * 24 * 60 * 60 * 1000));
    else if (period == 'M')
        priorDate = new Date(dt.getTime() - (chartShowDaysM * 24 * 60 * 60 * 1000));

    return formatDate(priorDate, format);
}