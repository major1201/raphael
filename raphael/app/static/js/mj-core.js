var mj={version:"1.0"};

mj.form={};
mj.form.getParams = function(id, separator) {
    if($.isBlank(separator)) separator = ",";
    var map = {};

    function putMap(n) {
        if (!mj.textField.isEmptyText(n)) {
            if($(n).attr("name")) {
                if(map[$(n).attr("name")] == undefined) {
                    map[$(n).attr("name")] = $(n).val();
                } else {
                    var tmp = map[$(n).attr("name")];
                    tmp += separator + $(n).val();
                    map[$(n).attr("name")] = tmp;
                }
            }
            else if($(n).attr("id")) map[$(n).attr("id")] = $(n).val();
        }
    }

    $.each($("#" + id).find("input"), function(i, n) {
        var type = $(n).attr("type");
        var value = $(n).val();
        if($.isNotBlank(value) && type=="text" || type=="password" || type=="hidden" || type == 'number' || type=="file") {
            putMap(n);
        }
    });
    $.each($("#" + id).find("input[type='checkbox']:checked"), function(i, n) {
        if(map[$(n).attr("name")] == undefined) {
            map[$(n).attr("name")] = $(n).val();
        } else {
            var tmp = map[$(n).attr("name")];
            tmp += separator + $(n).val();
            map[$(n).attr("name")] = tmp;
        }
    });
    $.each($("#" + id).find("input[type='radio']:checked"), function(i, n) {
        if($.isNotBlank($(n).val())) {
            putMap(n);
        }
    });
    $.each($("#" + id).find("select"), function(i, n) {
        var result = "";
        var obj;
        if($(n).attr("multiValue") == "1")
            obj = $(n).find("option");
        else
            obj = $(n).find("option:selected");
        $.each(obj, function(i, n) {
            result += $(n).val();
            if (i != (obj.length - 1))
                result += separator;
        });
        if($.isNotBlank(result)) {
            if($(n).attr("name")) {
                if(map[$(n).attr("name")] == undefined) {
                    map[$(n).attr("name")] = result;
                } else {
                    var tmp = map[$(n).attr("name")];
                    tmp += separator + result;
                    map[$(n).attr("name")] = tmp;
                }
            }
            else if($(n).attr("id")) map[$(n).attr("id")] = result;
        }
    });
    $.each($("#" + id).find("textArea"), function(i, n) {
        var value = $(n).val();
        if($.isNotBlank(value) && !mj.textField.isEmptyText(n)) {
            putMap(n);
        }
    });
    return map;
};

mj.textField={};
mj.textField.isEmptyText = function(obj) {
    return $(obj).attr("emptyText") == "1";
};

/*
 radio input tools
 */
mj.radio = {};
mj.radio.getVal = function(name) {
    var value = "";
    $.each($("input[name='" + name + "']:checked"), function(i,n) {
        value = $(n).val();
    });
    return value;
};
mj.radio.setVal = function(name,value) {
    $.each($("input[name='" + name + "']"), function(i,n) {
        if($(n).prop("checked")) $(n).prop("checked", false);
        if($(n).val() == value) $(n).prop("checked",true);
    });
};

mj.checkbox = {};
mj.checkbox.getVal = function(name) {
    var value = [];
    var obj = $("input[name='" + name + "']:checked");
    $.each(obj, function(i,n) {
        value.push($(n).val());
    });
    return value;
};
mj.checkbox.setVal = function(name,obj,sign) {
    if($.isBlank(sign)) sign = ",";
    var strArrays;
    if(typeof(obj) == 'string')
        strArrays = obj.split(sign);
    else
        strArrays = obj;
    var checkbox = $("input[name='" + name + "']").prop("checked", false);
    $.each(strArrays, function(i,n) {
        checkbox.filter("[value='"+n+"']").prop("checked", true);
    });
};
mj.checkbox.buildSelectAll = function(id,targetName) {
    $("#" + id).prop("checked", false);
    $("#" + id).click(function ()
    {
        if ($("#" + id).prop("checked"))
            $("input[type='checkbox'][name='" + targetName + "']:not(:disabled)").prop("checked", true);
        else
            $("input[type='checkbox'][name='" + targetName + "']:not(:disabled)").prop("checked", false);
    });
    $("input[type='checkbox'][name='"+targetName+"']").click(function(){
        if ($(this).prop("checked") == false)
            $("#" + id).prop("checked", false);
        if($("input[type='checkbox'][name='"+targetName+"']").length == $("input[type='checkbox'][name='"+targetName+"']:checked").length)
            $("#" + id).prop("checked", true);
    });
};

jQuery.extend({
isNull: function(s) {
    return s == undefined || s == null;
},
isNotNull: function(s) {
    return !$.isNull(s);
},
isBlank: function(s) {
    return $.isNull(s) || $.trim(s).length == 0;
},
isNotBlank: function(s) {
    return !$.isBlank(s);
},
isString: function(o) {
    return typeof o === 'string';
},
isArray: function(o) {
    return Object.prototype.toString.call(o) === '[object Array]';
},
isFunction: function(o) {
    return typeof o === 'function';
},
isEmail: function(s) {
    return s.match(/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/);
},
isAllNumber: function(s) {
    return s.match(/^[0-9]*$/)!=null;
},
trim2empty: function(s) {
    return $.isBlank(s) ? '' : s.trim();
},
hasChinese: function(s) {
    var patrn = /[\u4E00-\u9FA5]|[\uFE30-\uFFA0]/gi;
    return patrn.exec(s);
},
htmlEntities: function(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
},
mj_ajax: function(method, url, params, callBack, isBackground) {
    if (!isBackground) {$("body").isLoading({text:"Loading...",position:"overlay",class:"fa fa-spinner fa-pulse fa-2x fa-fw"});}
    $.ajax({
        url: url, type: method, data: params,
        success: function(result) {
            if (!isBackground) {$("body").isLoading("hide");}
            if (result == '__auth') {
                $.mj_alert('Authentication needed!');
            } else if (result == '__error') {
                $.mj_alert('Error occurs!');
            } else {
                callBack(result);
            }
        },
        error: function() {
            if (!isBackground) {$("body").isLoading("hide");}
            $.mj_alert("Error occurs during uploading.");
        }
    });
},
mj_websocket: function(path) {
    var ws_uri = [];
    var loc = window.location;
    ws_uri.push(loc.protocol === 'https:' ? 'wss://' : 'ws://');
    ws_uri.push(loc.host);
    ws_uri.push(path.startsWith('/') ? path : loc.pathname + (loc.pathname.endsWith('/') ? '' : '/') + path);
    return new WebSocket(ws_uri.join(''));
},
mj_setCookie: function(c_name,value,expiredays) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + expiredays);
    document.cookie=c_name + "=" + escape(value) + ((expiredays==null) ? "" : ";expires="+exdate.toGMTString());
},
mj_getCookie: function(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end=document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return ""
},
mj_pad: function(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
},
mj_keyEnter: function(e, fn) {
    if (e.keyCode == 13) {
        try {fn();} catch(ev) {console.log(ev)}
        return false;
    }
    return true;
},
mj_utc2local: function(date) {
    if ($.isBlank(date)) {return '';}
    var ud = new Date(date);
    var ld = new Date(Date.UTC(ud.getFullYear(), ud.getMonth(), ud.getDate(), ud.getHours(), ud.getMinutes(), ud.getSeconds(), ud.getMilliseconds()));
    return ld.getFullYear() + '-' + $.mj_pad(ld.getMonth() + 1, 2) + '-' + $.mj_pad(ld.getDate(), 2) + ' ' + $.mj_pad(ld.getHours(), 2) + ':' + $.mj_pad(ld.getMinutes(), 2) + ':' + $.mj_pad(ld.getSeconds(), 2);
},
mj_local2utc: function(date) {
    if ($.isBlank(date)) {return '';}
    var ld = new Date(date);
    return  ld.getUTCFullYear() + '-' + $.mj_pad(ld.getUTCMonth() + 1, 2) + '-' + $.mj_pad(ld.getUTCDate(), 2) + ' ' + $.mj_pad(ld.getUTCHours(), 2) + ':' + $.mj_pad(ld.getUTCMinutes(), 2) + ':' + $.mj_pad(ld.getUTCSeconds(), 2);
},
mj_alert: function(content, callBack, type) {
    swal({title: content, type: type, closeOnConfirm: false, html: true}, callBack);
},
mj_confirm: function(content, func) {
    swal({
        title: "Confirmation",
        text: content,
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        closeOnConfirm: false,
        html: true
    }, func);
},
mj_prompt: function(msg, dv, func) {
    swal({
        title: msg,
        type: "input",
        showCancelButton: true,
        closeOnConfirm: false,
        animation: "slide-from-top",
        inputValue: $.isBlank(dv) ? '' : dv,
        html: true
    },
    function(inputValue){
        if (inputValue === false) return false;
        if (inputValue === "") {
            swal.showInputError("You need to write something!");
            return false
        }
        func(inputValue);
    });
},
mj_close: function() {
    swal.close();
}
});

jQuery.fn.extend({
mj_preloadDialog: function() {
    var obj = this[0];
    var id = $(obj).attr("id");
    $("#_" + id + "_body").html($("#" + id + "_body").html());
    $("#" + id + "_body").remove();
    $("#_" + id + "_footer").html($("#" + id + "_footer").html());
    $("#" + id + "_footer").remove();
},
mj_show : function(title) {
    var obj = this[0];
    if (title != undefined) {
        var id = $(obj).attr("id");
        $("#" + id + "_title").html(title);
    }
    $(obj).modal({backdrop: 'static', keyboard: false});
},
mj_hide : function() {
    $(this[0]).modal("hide");
},
mj_preloadTable: function() {
    var obj = this[0];
    var id = $(obj).attr("id");

    var heading = $("#" + id + "_heading");
    var realHeading = $("#_" + id + "_heading");
    if ($(heading).length > 0) {
        $(realHeading).html($(heading).html());
        $(heading).remove();
    } else {
        if ($(realHeading).html().length === 0) {
            $(realHeading).remove();
        }
    }
    var prop = eval(id + "_prop");
    if ($.isNotBlank(prop.width)) {
        $(obj).css("width", prop.width);
        $(obj).parent().css("width", prop.width);
    }
    //style
    $.each(["striped", "bordered", "hover", "condensed"], function(i,o) {
        if ($.isBlank(prop[o]) || prop[o] == true) {$(obj).addClass("table" + o)}
    });
    var pagesize = [5, 10, 15, 20, 30, 50, 100, 200];
    var pagesize_html =[];
    $.each(pagesize, function(i, o) {
        pagesize_html.push('<option value="' + o + '"');
        if (o == prop.page_size) {pagesize_html.push(' selected="selected"')}
        pagesize_html.push(">" + o + "</option>");
    });
    $("#" + id + "_pagesize").html(pagesize_html.join(""));

    $("#" + id + "_orderby").val(prop.order_by);
    var col = eval(id + "_col");
    var head_append = [];
    head_append.push("<tr>");
    $.each(col, function(i, c) {
        head_append.push('<th style="');
        if ($.isNotBlank(c.width)) {head_append.push("width:" + c.width + ";");}
        if ($.isNotBlank(c.allow_sort) && c.allow_sort == true) {head_append.push("cursor:pointer;");}
        head_append.push('"');
        if ($.isNotBlank(c.allow_sort) && c.allow_sort == true) {head_append.push(" onclick=\"$('#" + id + "').mj_tableOrderBy(this, '" + c.prop + "');\"");}
        head_append.push(">");
        head_append.push(c.title);
        head_append.push("</th>");
    });
    head_append.push("</tr>");
    $("#" + id + "_head").html(head_append.join(""));
},
mj_query: function(page_index) {
    var obj = this[0];
    var id = $(obj).attr("id");
    var col = eval(id + "_col");
    var prop = eval(id + "_prop");
    if (page_index == undefined) {page_index = 1;}
    $("#" + id + "_pageindex").val(page_index);
    var pagesize = $("#" + id + "_pagesize").length > 0 ? $("#" + id + "_pagesize").val() : 0;
    var order_by = $("#" + id + "_orderby").val();
    var params = $.isBlank(prop.query_form) ? "{}" : JSON.stringify(mj.form.getParams(prop.query_form));
    $.mj_ajax('POST', prop.url, {"page_index":page_index, "page_size":pagesize, "order_by": order_by, "params": params}, function(result) {
        result = JSON.parse(result);
        var res = result.res;
        var dis = [];
        $.each(res, function(i, record) {
            dis.push("<tr");
            if ($.isBlank(record['_trstatus'])) {
                dis.push(">");
            } else {
                dis.push(" class='");
                dis.push(record['_trstatus']);
                dis.push("'>")
            }
            $.each(col, function(j, c) {
                var otext = record[c.prop] == null ? "" : record[c.prop];
                var text = c.js ? eval(c.js)(record) : otext;
                if (c.is_utc) {text = $.mj_utc2local(text); otext = text;}
                dis.push('<td align="');
                dis.push($.isNotBlank(c.align) ? c.align + '"' : 'center"');
                dis.push(' style="overflow:hidden;');
                if (c.wrap) {dis.push("word-break:break-all;")} else {dis.push("white-space:nowrap;");}
                dis.push('" ');
                if (c.allow_tag) {dis.push('title="' + otext + '"');}
                dis.push(">" + (c.html_entities ? $.htmlEntities(text) : text) + "</td>");
            });
            dis.push("</tr>");
        });
        $("#" + id + "_body").html(dis.join(""));

        if ($("#" + id + "_totalcount").length > 0) {
            $("#" + id + "_totalcount").text(result.count);
            var pageCount = (new Number(result.count) - 1) / new Number(pagesize) + 1;
            pageCount = parseInt(pageCount);
            $("#" + id + "_pagecount").text(pageCount);

            var pagination = [];
            pagination.push("<li id='" + id + "_prepage' class='disabled'><a id='" + id + "_prelink' href='javascript:void(0)'>&laquo;</a></li>");
            if (pageCount > 0) {
                var diff = 2 + ((pageCount - page_index) < 2 ? 2 - (pageCount - page_index) : 0);
                var lbound = page_index - diff < 1 ? 1 : page_index - diff;
                diff = 2 + (page_index < 3 ? 3 - page_index : 0);
                var ubound = page_index + diff > pageCount ? pageCount : page_index + diff;
                for (var i = lbound; i <= ubound; i++) {
                    if (i == page_index) {
                        pagination.push("<li class='active'><a href='javascript:void(0);'>" + i + "</a></li>");
                    } else {
                        pagination.push("<li><a href='javascript:void(0);' onclick='$(\"#" + id + "\").mj_query(" + i + ");'>" + i + "</a></li>");
                    }
                }
            }
            pagination.push("<li id='" + id + "_nextpage' class='disabled'><a id='" + id + "_nextlink' href='javascript:void(0)'>&raquo;</a></li>");
            $("#" + id + "_pagination").html(pagination.join(""));
            if (page_index > 1) {
                $("#" + id + "_prepage").removeClass("disabled");
                $("#" + id + "_prelink").attr("onclick", '$("#' + id + '").mj_query(' + (page_index - 1) + ");");
            }
            if (page_index < pageCount) {
                $("#" + id + "_nextpage").removeClass("disabled");
                $("#" + id + "_nextlink").attr("onclick", '$("#' + id + '").mj_query(' + (page_index + 1) + ");");
            }
        }
        if (prop.after_query) {eval(prop.after_query)(res);}
    });
},
mj_currentPage : function() {
    var obj = this[0];
    var id = $(obj).attr("id");
    return $("#" + id + "_pageindex").val();
},
mj_tableOrderBy: function(th, prop) {
    var ascArrow = '<b class="caret-up"></b>';
    var descArrow = '<b class="caret"></b>';
    var obj = this[0];
    var id = $(obj).attr("id");
    //clear style
    $("#" + id + " th").each(function(i, o) {
        var html = $(o).html().toString();
        var ascIndex = html.indexOf(ascArrow);
        var descIndex = html.indexOf(descArrow);
        if (ascIndex > 0) {
            $(o).html(html.substr(0, ascIndex));
        }
        if (descIndex > 0) {
            $(o).html(html.substr(0, descIndex));
        }
    });
    var orderByInput = $("#" + id + "_orderby");
    var currOrderBy = $(orderByInput).val();
    var asc = currOrderBy != prop;
    $(orderByInput).val(prop + (asc ? "" : " desc"));
    $(th).html($(th).html() + (asc ? ascArrow : descArrow));
    $(obj).mj_query();
},
mj_submit: function(method, url, callBack) {
    var obj = this[0];
    var id = $(obj).attr("id");
    var params = mj.form.getParams(id, ",");
    $.mj_ajax(method, url, params, callBack);
},
mj_setPicker: function(datestr) {
    var obj = this[0];
    var id = $(obj).attr("id");
    $('#' + id + '_text').val(datestr);
    $('#' + id + '_local').val(datestr);
    $('#' + id + '_utc').val($.mj_local2utc(datestr));
}
});