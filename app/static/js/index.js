function getPercent(current, total) {
    return current / total * 100;
}

let loading = document.getElementById("chart_loading")
loading.hidden = false

fetch("api/repositories").then(
    function fetchResponse(response) {
        response.json().then(function fetchResult(result) {
            let total_value = 0
            for (let key in result) {
                total_value += result[key];
            }

            loading.hidden = true

            let colunms = []
            for (let key in result) {
                const value = getPercent(result[key], total_value)
                colunms.push([key, value])
            }

            bb.generate({
                data: {
                    columns: colunms,
                    colors: language,
                    type: "pie"
                },
                pie: {
                    label: {
                        format: function (value, ratio, id) {
                            const round_value = value.toFixed(1);
                            return `${id}\n(${round_value}%)`;
                        }
                    }
                },
                legend: {
                    show: true
                },
                bindto: "#programing_chart"
            });
        })
    }
)