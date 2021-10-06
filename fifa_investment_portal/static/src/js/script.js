odoo.define("fifa_investment_portal.Chart", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var rpc = require('web.rpc');
    require("web.dom_ready");

    publicWidget.registry.Chart = publicWidget.Widget.extend({
        selector: ".funds-chart",

        start: function () {
            var user_id = $("#user_id").val();
            var self = this;
            var model = 'res.fifa.investment.fund.partner.investments';
            var domain = [['partner.id', '=', user_id]];
            var fields = [];
            rpc.query({
                model: model,
                method: 'search_read',
                args: [domain, fields],
            }).then(function (d) {
                var fundsAmmountList = []
                var FundsList = []
                if (d.length === 0){
                    $('.no-funds').removeClass('d-none');
                }
                d.forEach(element => fundsAmmountList.push(element.amount_invested));
                d.forEach(element => FundsList.push(element.investment_fund[1] + ' - ' + element.amount_invested +' '+ element.currency[1]));
                var bgList = []
                for (var i = 0; i < FundsList.length; i++) {
                    bgList.push(self.random_rgba());
                }
                var ctx = $('#myChart');
                const data = {
                    labels: FundsList,
                    datasets: [{
                        label: 'Funds',
                        data: fundsAmmountList,
                        backgroundColor: bgList,
                        hoverOffset: 4
                    }]
                };
                var myChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: data,
                });
            });
        },
        random_rgba: function () {
            var o = Math.round, r = Math.random, s = 255;
            return 'rgba(' + o(r() * s) + ',' + o(r() * s) + ',' + o(r() * s) + ',' + r().toFixed(1) + ')';
        },
    });
});


odoo.define("fifa_investment_portal.ChartDis", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var rpc = require('web.rpc');
    require("web.dom_ready");

    publicWidget.registry.ChartDis = publicWidget.Widget.extend({
        selector: ".fund-dis",

        start: function () {
            var fund_id = $("#fund_id").val();
            var self = this;
            var model = 'res.fifa.investment.fund.partner.investments';
            var domain = [['id', '=', fund_id]];
            var fields = [];
            rpc.query({
                model: model,
                method: 'search_read',
                args: [domain, fields],
            }).then(function (d) {
                var user_id = $("#user_id").val();
                var model2 = 'res.fifa.investment.fund.partner.share'
                var share_ids = d[0].partner_fifa_investments
                var domain2 = [
                    ['id', 'in', share_ids]
                ];
                var fields2 = [];
                rpc.query({
                    model: model2,
                    method: 'search_read',
                    args: [domain2, fields2],
                }).then(function (rdata) {
                    var ammount = []
                    var labels = []
                    rdata.forEach(element => ammount.push(element.amount_owned));
                    rdata.forEach(element => labels.push(element.partner_investment_id[1].split("-")[0] + ' - ' + element.fifa_lead[1] + ' - ' + element.amount_owned.toFixed(2) + ' - ' + element.currency[1]));
                    var bgList = []
                    for (var i = 0; i < labels.length; i++) {
                        bgList.push(self.random_rgba());
                    }
                    var ctx = $('#myChart');
                    const data = {
                        labels: labels,
                        datasets: [{
                            label: 'Funds Shares',
                            data: ammount,
                            backgroundColor: bgList,
                            hoverOffset: 4
                        }]
                    };
                    var myChart = new Chart(ctx, {
                        type: 'doughnut',
                        data: data,
                    });
                })
            });
        },
        random_rgba: function () {
            var o = Math.round, r = Math.random, s = 255;
            return 'rgba(' + o(r() * s) + ',' + o(r() * s) + ',' + o(r() * s) + ',' + r().toFixed(1) + ')';
        },
    });
});
