// 随机色值
window.getRandomColor = function () {
    return '#' +
        (function (color) {
            return (color += '0123456789abcdef' [Math.floor(Math.random() * 16)]) &&
                (color.length == 6) ? color : arguments.callee(color);
        })('');
}

$(function () {

        $("#golabel_active").on("click", function () {
            getJz(function () {
                $("#history_yes").click();
                $("#feng_yes").click();
            });

            // $("#history_yes").click();
        })
        // 默认情况下 全局配置
        //        var golable = '{data: ["23"],fm: [{"name": "fuhe_start","value": "1"}, {"name": "fuhe_end","value": "2"}, {"name": "shuitou_start","value": "3"}, {"name": "shuitou_end","value": "4" }, {"name": "startTime", "value": "2017-11-06 00:00:00"}, {"name": "endTime","value": "2017-11-06 10:59:22"}, {"name": "monit_period","value": "1"}, {"name": "multi_num","value": "1"}, {"name": "multi_num","value": "1"}]}';
        var golable = {
            data: [],
            fm: []
        };

        function getJz(foo) {
            var jz = [];
            var $jzs = $("#jz_options").find("a.active");
            Array.apply(null, $jzs).forEach(function (item) {
                jz.push(item.getAttribute("data-jv"));
            })
            golable.data = JSON.stringify(jz);
            golable.fm = JSON.stringify($("#other_fm").serializeArray())

            $.ajax({
                url: "/myindex",
                data: {
                    golable: JSON.stringify(golable)
                },
                type: 'POST',
                dataType: 'json',
                complete: function () {
                    foo();
                },
                success: function (res) {
                    // console.log(res)
                },
                error: function (err) {
                    (err);
                }
            })
        }


        // 峰峰值
        function fengRender(fengChart, resoult) {
            // 默认峰峰值内容
            function fengOptions(id, data) {
                return {
                    chart: {
                        renderTo: id,
                        zoomType: 'x',
                    },
                    xAxis: {
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            millisecond: '%H:%M:%S.%L',
                            second: '%H:%M:%S',
                            minute: '%H:%M',
                            hour: '%H:%M',
                            day: '%m-%d',
                            week: '%m-%d',
                            month: '%Y-%m',
                            year: '%Y'
                        }
                    },
                    tooltip: {
                        dateTimeLabelFormats: {
                            millisecond: '%H:%M:%S.%L',
                            second: '%H:%M:%S',
                            minute: '%H:%M',
                            hour: '%H:%M',
                            day: '%Y-%m-%d',
                            week: '%m-%d',
                            month: '%Y-%m',
                            year: '%Y'
                        }
                    },
                    title: {
                        text: '趋势图'
                    },
                    plotOptions: {
                        color: "#ff00ff",
                    },
                    yAxis: {
                        title: {
                            text: "峰值"
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    series: data
                }
            }
            var d = ["shangx_ffz", "shangy_ffz"];
            var dnames = ["上导X摆度峰峰值", "上导Y摆度峰峰值"];
            var isFSend = true;
            function initSendFeng() {
                $.ajax({
                    url: '/sendFengData',
                    type: "GET",
                    // data: {
                    //     fengFields: JSON.stringify(d),
                    //     golable: JSON.stringify(golable)
                    // },
                    dataType: 'json',
                    complete:function(){
                        fengGetInterver()
                    },
                    success: function (res) {
                        var datas = fengZhiData(res);
                        $.fengChart = new Highcharts.Chart(fengOptions('ssj', datas));
                    },
                    error: function (err) {
                        console.log(err);
                    }
                })
            }
            initSendFeng()
            function fengGetInterver() {
                isFSend?"":clearInterval($.fengTime);
                $.fengTime = setInterval(function () {
                    $.ajax({
                        url: "/getFengData",
                        type: 'POST',
                        data: {
                            fengFields: JSON.stringify(d),
                            golable: JSON.stringify(golable)
                        },
                        success: function (res) {
                            oneTimeRenderFeng($.fengChart, res)
                        },
                        error: function (err) {
                            console.log(err)
                        }
                    })
                }, 1000)
            }
            // 一秒添加一个点到chart
            function oneTimeRenderFeng(chart, res) {
                var seriesLen = chart.length;
                Array.apply(null, chart.series).forEach(function (p, k) {
                    var x = new Date(res.feng_time).getTime(),
                        y = res.feng_data[k];
                    p.addPoint([x, y], true, true)
                })
            }
            $("#feng_yes").on('click', function () {
                var params = $(this).parent().siblings('a.active');
                if (params.length > 0) {
                    d = [];
                    dnames = [];
                    isFSend = false;
                    Array.apply(null, params).forEach(function (item) {
                        d.push($(item).data("fv"));
                        dnames.push($(item).text())
                    })
                    $.ajax({
                        url: '/sendFengData',
                        data: {
                            fengFields: JSON.stringify(d),
                            golable: JSON.stringify(golable)
                        },
                        dataType: 'json',
                        type: "POST",
                        complete: function () {
                            fengGetInterver()
                        },
                        success: function (res) {
                            var datas = fengZhiData(res);
                            $.fengChart = new Highcharts.Chart(fengOptions('ssj', datas));
                        },
                        error: function (err) {
                            console.log(err);
                        }
                    })


                } else {
                    alert("您没有选择参数")
                }
            })


            // 返回[time,data]数组
            function fengZhiData(res) {
                var times = res.fengTime;
                var values = res.postFengData;
                var data = [];
                for (var k = 0, klen = d.length; k < klen; k++) {
                    var idata = [];
                    for (var i = 0, len = values.length; i < len; i++) {
                        var timespace = new Date(times[i]).getTime();
                        idata.push([timespace, values[i][k]])
                    }
                    data.push({
                        name: dnames[k],
                        data: Array.prototype.slice.call(idata)
                    });
                }
                return data;
            }

        }
        fengRender()

        //频谱
        function pprender() {
            $.ppnames = ["上导X摆度倍频值", "上导Y摆度倍频值"]
            $("#pinp_ci").on('click', function () {
                var params = $(this).parent().siblings('a.active');
                if (params.length > 0) {

                    var d = [];
                    var namesT = [];
                    Array.apply(null, params).forEach(function (item) {
                        d.push($(item).data("fv"));
                        namesT.push($(item).text());
                    })

                    $.ajax({
                        url: '/sendXfsData',
                        data: {
                            xfsFields: JSON.stringify(d),
                            golable: JSON.stringify(golable)
                        },
                        dataType: 'json',
                        type: "POST",
                        complete: function () {
                            if (ppcharts.length > 0) {
                                clearInterval(window.ti)
                                $.ppnames = namesT;
                                setTRender(ppcharts)
                            }
                        },
                        success: function (data) {
                            var res = settXNum(data.postXfsData);
                            creatPPTag(res.length, res, data)
                        },
                        error: function (err) {
                            console.log(err);
                        }
                    })

                } else {
                    alert("您没有选择参数")
                }
            })
            $.ajax({
                url: '/sendXfsData',
                type: "GET",
                dataType: "json",
                async: false,
                complete: function () {
                    setTRender(ppcharts);
                },
                success: function (data) {
                    var res = settXNum(data.postXfsData);
                    creatPPTag(res.length, res, data)

                }
            })
        }

        function initOptions(id) {
            return {
                chart: {
                    renderTo: id,
                    zoomType: 'x',
                },
                title: {
                    text: '频谱'
                },
                plotOptions: {
                    color: "#ff00ff",
                    // series: {
                    //     zones: [{
                    //         value: 0,
                    //     }, 
                    //         value: 3,
                    //     }, {
                    //         color: "red "
                    //     }, ]
                    // }
                },
                yAxis: {
                    title: {
                        text: "幅值"
                    }
                },
                credits: {
                    enabled: false
                },
                series: []
            }
        }

        var ppcharts; //charts对象
        function creatPPTag(len, res, data) {
            ppcharts = [];
            var parent = $('#main_r_i_chart')
            parent.children().remove();
            for (var i = 0; i < len; i++) {
                var temp = $(' <div id="pp' + i + '" style="min-width:400px;height:200px;"></div');
                parent.append(temp);
            }
            for (var i = 0, len = res.length; i < len; i++) {
                var getOptions = initOptions("pp" + i);
                getOptions.title.text = data.xfsTime;
                ppcharts.push(new Highcharts.Chart(getOptions));
                // console.log(i + " ---- " + ppcharts[i])
                ppcharts[i].setTitle({
                    text: $.ppnames[i]
                }, {
                    text: data.xfsTime
                })
                ppcharts[i].addSeries({
                    //                            name: fields[i],
                    data: res[i],
                    color: window.getRandomColor()
                })
            }
        }

        function setTRender(chartlist) {
            Array.apply(null, $.ppnames).forEach(function (item, key) {
                chartlist[key].setTitle({
                    text: item
                })
            })
            window.ti = setInterval(function () {
                $.ajax({
                    url: "/getXfsData",
                    type: "GET",
                    data: {},
                    async: false,
                    dataType: "json",
                    success: function (data) {
                        var d = settXNum(data.postXfsData);
                        for (var j = 0; j < d.length; j++) {
                            chartlist[j].setTitle(null, {
                                text: data.xfsTime
                            })
                            chartlist[j].series[0].setData(d[j]);
                        }
                    },
                    error: function (err) {
                        alert("error");
                        console.log(err);
                    }
                });
            }, 1000)
        }
        // x轴横坐标显示范围数据处理
        function settXNum(arr) {
            var newArrTb = [];
            for (var i = 0; i < arr.length; i++) {
                var iarr = [];
                for (var j = 0; j < arr[i].length; j++) {
                    var k = j / 8;
                    var jarr = [];
                    jarr.push(k);
                    jarr.push(arr[i][j]);
                    iarr.push(jarr);
                }
                newArrTb.push(iarr);
            }
            return newArrTb;
        }
        pprender();

        // 原始数据
        function renderHistory() {
            function rawOptions(id, data) {
                return {
                    chart: {
                        renderTo: id,
                        zoomType: 'x',
                    },
                    title: {
                        text: '原始数据'
                    },
                    xAxis: {
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            millisecond: '%H:%M:%S.%L',
                            second: '%H:%M:%S',
                            minute: '%H:%M',
                            hour: '%H:%M',
                            day: '%m-%d',
                            week: '%m-%d',
                            month: '%Y-%m',
                            year: '%Y'
                        }
                    },
                    tooltip: {
                        dateTimeLabelFormats: {
                            millisecond: '%H:%M:%S.%L',
                            second: '%H:%M:%S',
                            minute: '%H:%M',
                            hour: '%H:%M',
                            day: '%Y-%m-%d',
                            week: '%m-%d',
                            month: '%Y-%m',
                            year: '%Y'
                        }
                    },
                    plotOptions: {
                        color: "#ff00ff",
                    },
                    yAxis: {
                        title: {
                            text: "原始值"
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    series: data
                }
            }
            var d = ["shangx", "shangy"];
            var dnames = ["上导X摆度", "上导Y摆度"];
            $.ajax({
                url: '/sendRawData',
                data: {
                    rawFields: JSON.stringify(d),
                    golable: golable
                },

                dataType: 'json',
                type: "POST",
                success: function (res) {
                    var datas = rawZhiData(res);
                    new Highcharts.Chart(rawOptions('qbp', datas));
                },
                error: function (err) {
                    console.log(err);
                }
            })

            $("#history_yes").on('click', function () {
                var params = $(this).parent().siblings('a.active');
                if (params.length > 0) {
                    d = [];
                    dnames = [];
                    Array.apply(null, params).forEach(function (item) {
                        d.push($(item).data("fv"));
                        dnames.push($(item).text())
                    })
                }

                $.ajax({
                    url: '/sendRawData',
                    data: {
                        rawFields: JSON.stringify(d),
                        golable: golable
                    },
                    dataType: 'json',
                    type: "POST",
                    success: function (res) {
                        var datas = rawZhiData(res);
                        new Highcharts.Chart(rawOptions('qbp', datas));
                    },
                    error: function (err) {
                        console.log(err);
                    }
                })
            })
            // 返回[time,data]数组
            function rawZhiData(res) {
                var times = res.rawTime;
                var values = res.postRawData;

                var data = [];
                for (var k = 0, klen = d.length; k < klen; k++) {
                    var idata = [];
                    for (var i = 0, len = values.length; i < len; i++) {
                        // idata.push([times[i], values[i][k]])
                        var timespace = new Date(times[i]).getTime();
                        idata.push([timespace, values[i][k]])
                    }
                    data.push({
                        name: dnames[k],
                        data: Array.prototype.slice.call(idata)
                    });
                }
                return data;
            }
        }

        renderHistory();

        // 健康值
        function renderHealthy() {
            function returnHOptions(datas) {
                return {
                    chart: {
                        renderTo: "healthy_show",
                    },
                    xAxis: {
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            millisecond: '%H:%M:%S.%L',
                            second: '%H:%M:%S',
                            minute: '%H:%M',
                            hour: '%H:%M',
                            day: '%m-%d',
                            week: '%m-%d',
                            month: '%Y-%m',
                            year: '%Y'
                        }
                    },
                    tooltip: {
                        dateTimeLabelFormats: {
                            millisecond: '%H:%M:%S.%L',
                            second: '%H:%M:%S',
                            minute: '%H:%M',
                            hour: '%H:%M',
                            day: '%Y-%m-%d',
                            week: '%m-%d',
                            month: '%Y-%m',
                            year: '%Y'
                        }
                    },
                    plotOptions: {
                        series: {
                            showInLegend: true
                        }
                    },
                    tooltip: {
                        split: false,
                        shared: true
                    },
                    rangeSelector: {
                        buttons: [{
                            count: 1,
                            type: 'minute',
                            text: '1M'
                        }, {
                            count: 5,
                            type: 'minute',
                            text: '5M'
                        }, {
                            type: 'all',
                            text: 'All'
                        }],
                        inputEnabled: false,
                        selected: 0
                    },
                    title: {
                        text: null
                    },
                    tooltip: {
                        split: false
                    },
                    exporting: {
                        enabled: false
                    },
                    series: datas
                }
            }
            var arr = [];
            $.ajax({

                url: '/sendIsofData',
                dataType: 'json',
                complete: function () {

                },
                success: function (res) {
                    var isof_time = res.isof_time;
                    var isof_z = res.isof_z;
                    for (var i = 0, len = isof_time.length; i < len; i++) {
                        var temp = [];
                        temp.push(new Date(isof_time[i]).getTime());
                        temp.push(isof_z[i])
                        arr.push(temp);
                    }
                    var datas = [{
                        name: "健康度",
                        data: arr
                    }]
                    var hCharts = new Highcharts.Chart(returnHOptions(datas));
                    setTimeout(function () {
                        setInterRenter(hCharts)
                    }, 3000)

                }
            })

            function setInterRenter(hc) {
                setInterval(function () {
                    $.ajax({
                        url: '/getIsofData',
                        dataType: 'json',
                        //async: false,
                        success: function (res) {
                            var x = new Date(res.isof_time).getTime(), // current time
                                y = res.isof_z;
                            hc.series[0].addPoint([x, y], true, true);
                        }
                    })
                }, 1000);
            }
        }
        renderHealthy();
    })



    // myjs
    ! function ($) {
        $(".main-ris-tip").on("click", "i", function () {
            var options = $(this).parent().siblings(".mris-options");
            if (!options.hasClass("_a")) {
                options.slideDown("slow").addClass("_a");
                $(this).removeClass("icon-jiantouxia").addClass("icon-jiantoushang");
            } else {
                options.slideUp("slow").removeClass("_a");
                $(this).removeClass("icon-jiantoushang").addClass("icon-jiantouxia");
            }
        })
        $(".mris-options").on("click", 'a', function () {
            if ($(this).hasClass('active')) {
                $(this).removeClass("active");
            } else {
                $(this).addClass("active");
            }
        })
        $(".jz-options").on("click", 'a', function () {
            if ($(this).hasClass('active')) {
                $(this).removeClass("active");
            } else {
                $(this).addClass("active");
            }
        })
        $(".reset-btn").on('click', function () {
            $(this).parent().siblings("a").removeClass('active');
        })


    }(jQuery)