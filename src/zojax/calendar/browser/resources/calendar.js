$(document).ready(function() {

            var view="month";
            var DATA_FEED_URL = CalendarAPI_URL;
            var op = {
                view: view,
                theme:3,
                showday: new Date(),
                EditCmdhandler:Edit,
                DeleteCmdhandler:Delete,
                ViewCmdhandler:View,
                onWeekOrMonthToDay:wtd,
                onBeforeRequestData: cal_beforerequest,
                onAfterRequestData: cal_afterrequest,
                onRequestDataError: cal_onerror,
                autoload:true,
                url: DATA_FEED_URL + "list",
                quickAddUrl: DATA_FEED_URL + "add",
                quickUpdateUrl: DATA_FEED_URL + "update",
                quickDeleteUrl: DATA_FEED_URL + "remove",
                readonly: CalendarAPI_readonly,
                zone: userTimezone
            };
            var $dv = $("#calhead");
            var _MH = document.documentElement.clientHeight;
            var dvH = $dv.height() + 2;
            op.height = _MH - dvH;
            op.eventItems =[];

            var p = $("#gridcontainer").bcalendar(op).BcalGetOp();
            if (p && p.datestrshow) {
                $("#txtdatetimeshow").text(p.datestrshow);
            }
            $("#caltoolbar").noSelect();

            $("#hdtxtshow").datepicker({ picker: "#txtdatetimeshow", showtarget: $("#txtdatetimeshow"),
            onReturn:function(r){
                            var p = $("#gridcontainer").gotoDate(r).BcalGetOp();
                            if (p && p.datestrshow) {
                                $("#txtdatetimeshow").text(p.datestrshow);
                            }
                     }
            });
            function cal_beforerequest(type)
            {
                var t="Loading data...";
                switch(type)
                {
                    case 1:
                        t="Loading data...";
                        break;
                    case 2:
                    case 3:
                    case 4:
                        t="The request is being processed ...";
                        break;
                }
                $("#errorpannel").hide();
                $("#loadingpannel").html(t).show();
            }
            function cal_afterrequest(type)
            {
                switch(type)
                {
                    case 1:
                        $("#loadingpannel").hide();
                        break;
                    case 2:
                    case 3:
                    case 4:
                        $("#loadingpannel").html("Success!");
                        window.setTimeout(function(){ $("#loadingpannel").hide();},2000);
                    break;
                }

            }
            function cal_onerror(type,data)
            {
                $("#errorpannel").show();
            }
            function Edit(data)
            {
               var eurl="edit.html?id={0}&start={2}&end={3}&isallday={4}&title={1}";
               if (userTimezone) {
                 eurl = eurl + '&timezone=' + userTimezone;
               }
                if(data)
                {
                    var url = StrFormat(eurl,data);
                    OpenModelWindow(url,{ width: 600, height: 550, caption:"Manage  The Calendar",onclose:function(){
                       $("#gridcontainer").reload();
                    }});
                }
            }
            function View(data, pos, ss)
            {

                var str = "";
                $.each(data, function(i, item){
                    str += "[" + i + "]: " + item + "\n";
                });
                if (data != null) {
                    var csbuddle = '<div id="bbit-cs-buddle" style="z-index: 180; width: 400px;visibility:hidden;" class="bubble"><table class="bubble-table" cellSpacing="0" cellPadding="0"><tbody><tr><td class="bubble-cell-side"><div id="tl1" class="bubble-corner"><div class="bubble-sprite bubble-tl"></div></div><td class="bubble-cell-main"><div class="bubble-top"></div><td class="bubble-cell-side"><div id="tr1" class="bubble-corner"><div class="bubble-sprite bubble-tr"></div></div>  <tr><td class="bubble-mid" colSpan="3"><div style="overflow: hidden" id="bubbleContent1"><div><div></div><div class="cb-root"><table class="cb-table" cellSpacing="0" cellPadding="0"><tbody><tr><td class="cb-value"><div class="textbox-fill-wrapper"><div class="textbox-fill-mid"><div id="bbit-cs-what" title="' + i18n.xgcalendar.click_to_detail + '" class="textbox-fill-div lk" style="cursor:pointer;"></div></div></div></td></tr><tr><td class=cb-value><div id="bbit-cs-buddle-timeshow"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-location"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-description"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-attendeers"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-eventUrl"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-CName"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-CEmail"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-CPhone"></div></td></tr><tr><td class=cb-value><div id="bbit-cs-body"></div></td></tr></tbody></table> </div></div></div><tr><td><div id="bl1" class="bubble-corner"><div class="bubble-sprite bubble-bl"></div></div><td><div class="bubble-bottom"></div><td><div id="br1" class="bubble-corner"><div class="bubble-sprite bubble-br"></div></div></tr></tbody></table><div id="bubbleClose2" class="bubble-closebutton"></div><div id="prong1" class="prong"><div class=bubble-sprite></div></div></div>';
                    var bud = $("#bbit-cs-buddle");

                    if (bud.length == 0) {
                        bud = $(csbuddle).appendTo(document.body);
                        var closebtn = $("#bubbleClose2").click(function() {
                            $("#bbit-cs-buddle").css("visibility", "hidden");
                        });

                        bud.click(function(e) { return false });
                    }

                    if (pos.hide) {
                        $("#prong1").hide()
                    } else {
                        $("#prong1").show()
                    }

                    //location
                    if (data[9]) {
                        $("#bbit-cs-location").css("display", "block").html(data[9]);
                    }
                    //description
                    if (data[10]) {
                        $("#bbit-cs-description").css("display", "block").html(data[10]);
                    }
                    //attendeers
                    if (data[11]) {
                    	$("#bbit-cs-attendeers").css("display", "block").html(decodeURIComponent(data[11]))
                    }
                    //eventUrl
                    if (data[12]) {
                        $("#bbit-cs-eventUrl").css("display", "block").html('<a href="'+data[12]+'">'+data[12]+'</a>');
                    }
                    //CName
                    if (data[13]) {
                        $("#bbit-cs-CName").css("display", "block").html(data[13]);
                    }
                    //CEmail
                    if (data[14]) {
                        $("#bbit-cs-CEmail").css("display", "block").html('<a href="mailto:'+data[14]+'">'+data[14]+'</a>');
                    }
                    //CPhone
                    if (data[15]) {
                        $("#bbit-cs-CPhone").css("display", "block").html(data[15]);
                    }
                    //body
                    if (data[16]) {
                        $("#bbit-cs-body").css("display", "block").html(data[16]);
                    }

                    var ts = $("#bbit-cs-buddle-timeshow").html(ss.join(""));
                    $("#bbit-cs-what").css("display", "block").html('<a href="'+Calendar_URL+data[0]+'">'+data[1]+'</a>');
                    bud.data("cdata", data);
                    bud.css({ "visibility": "visible", left: pos.left, top: pos.top });

                    $(document).one("click", function() {
                        $("#bbit-cs-buddle").css("visibility", "hidden");
                    });

                    $("#bbit-cs-buddle").find('a').click(function () {window.open(this.href)});
                }
                return false;

            }
            function Delete(data,callback)
            {

                $.alerts.okButton="Ok";
                $.alerts.cancelButton="Cancel";
                hiConfirm("Are You Sure to Delete this Event", 'Confirm',function(r){ r && callback(0);});
            }
            function wtd(p)
            {
               if (p && p.datestrshow) {
                    $("#txtdatetimeshow").text(p.datestrshow);
                }
                $("#caltoolbar div.fcurrent").each(function() {
                    $(this).removeClass("fcurrent");
                })
                $("#showdaybtn").addClass("fcurrent");
            }
            //to show day view
            $("#showdaybtn").click(function(e) {
                //document.location.href="#day";
                $("#caltoolbar div.fcurrent").each(function() {
                    $(this).removeClass("fcurrent");
                })
                $(this).addClass("fcurrent");
                var p = $("#gridcontainer").swtichView("day").BcalGetOp();
                if (p && p.datestrshow) {
                    $("#txtdatetimeshow").text(p.datestrshow);
                }
            });
            //to show week view
            $("#showweekbtn").click(function(e) {
                //document.location.href="#week";
                $("#caltoolbar div.fcurrent").each(function() {
                    $(this).removeClass("fcurrent");
                })
                $(this).addClass("fcurrent");
                var p = $("#gridcontainer").swtichView("week").BcalGetOp();
                if (p && p.datestrshow) {
                    $("#txtdatetimeshow").text(p.datestrshow);
                }

            });
            //to show month view
            $("#showmonthbtn").click(function(e) {
                //document.location.href="#month";
                $("#caltoolbar div.fcurrent").each(function() {
                    $(this).removeClass("fcurrent");
                })
                $(this).addClass("fcurrent");
                var p = $("#gridcontainer").swtichView("month").BcalGetOp();
                if (p && p.datestrshow) {
                    $("#txtdatetimeshow").text(p.datestrshow);
                }
            });

            $("#showreflashbtn").click(function(e){
                $("#gridcontainer").reload();
            });

            //Add a new event
            $("#faddbtn").click(function(e) {
                var url ="edit.html";
                OpenModelWindow(url,{ width: 500, height: 550, caption: "Create New Calendar",onclose:function(){
                       $("#gridcontainer").reload();
                    }});
            });
            //go to today
            $("#showtodaybtn").click(function(e) {
                var p = $("#gridcontainer").gotoDate().BcalGetOp();
                if (p && p.datestrshow) {
                    $("#txtdatetimeshow").text(p.datestrshow);
                }
            });
            //previous date range
            $("#sfprevbtn").click(function(e) {
                var p = $("#gridcontainer").previousRange().BcalGetOp();
                if (p && p.datestrshow) {
                    $("#txtdatetimeshow").text(p.datestrshow);
                }

            });
            //next date range
            $("#sfnextbtn").click(function(e) {
                var p = $("#gridcontainer").nextRange().BcalGetOp();
                if (p && p.datestrshow) {
                    $("#txtdatetimeshow").text(p.datestrshow);
                }
            });

});
