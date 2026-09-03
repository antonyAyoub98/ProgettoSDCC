const form = document.getElementById("prediction-form");
const resultDiv = document.getElementById("result");
const historyBody = document.getElementById("history-body");
const refreshButton = document.getElementById("refresh-history");

form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const data = {
        Temperature:
            parseFloat(
                document.getElementById("temperature").value
            ),
        Light:
            parseFloat(
                document.getElementById("light").value
            ),
        Sound:
            parseFloat(
                document.getElementById("sound").value
            ),
        CO2:
            parseFloat(
                document.getElementById("co2").value
            )
    };

    try {

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error("Errore durante la predizione");
        }
        const result = await response.json();

        resultDiv.innerHTML =
            `Persone previste: ${result.prediction}`;

        resultDiv.classList.remove("hidden");
        loadHistory(); //aggiorna lo storico
    } catch (error) {

        resultDiv.innerHTML =
            "Errore durante la predizione.";

        resultDiv.classList.remove("hidden");

        console.error(error);

    }

});

async function loadHistory() {
    try {
        const response =
            await fetch("/predictions?limit=20");
        if (!response.ok) {
            throw new Error(
                "Errore nel recupero dello storico"
            );
        }

        const data = await response.json();
        historyBody.innerHTML = "";

        data.predictions.forEach(prediction => {
            const row =
                document.createElement("tr");

            let timestamp = "-";
            if (prediction.timestamp) {
                timestamp =
                    new Date(
                        prediction.timestamp
                    ).toLocaleString();

            }

            row.innerHTML = `

                <td>${timestamp}</td>

                <td>
                    ${prediction.sensori.Temperature}
                </td>

                <td>
                    ${prediction.sensori.Light}
                </td>

                <td>
                    ${prediction.sensori.Sound}
                </td>

                <td>
                    ${prediction.sensori.CO2}
                </td>

                <td>
                    <strong>
                        ${prediction.numero_persone_predetto}
                    </strong>
                </td>

            `;
            historyBody.appendChild(row);
        });


    } catch (error) {

        console.error(
            "Errore storico:",
            error
        );

    }

}

refreshButton.addEventListener(
    "click",
    loadHistory
);

//mi da lo storico appena apre la pagina
loadHistory();