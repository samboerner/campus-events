const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
];

const wrapper = document.querySelector("#cal");
const modalContainer = wrapper.shadowRoot.querySelector("#modal-container");
const e = {
    monthYear: wrapper.shadowRoot.getElementById("month-year"),
    prevMonth: wrapper.shadowRoot.getElementById("prev-month"),
    nextMonth: wrapper.shadowRoot.getElementById("next-month"),
    dates: wrapper.shadowRoot.getElementById("dates"),
}

const date = new Date();

function updateDates() {
    const year = date.getFullYear();
    const month = date.getMonth();

    e.monthYear.innerHTML = months[month] + " " + year;

    const firstDOW = new Date(year, month, 1).getDay();
    const lastDOW = new Date(year, month + 1, 0).getDay();
    const thisLastDay = new Date(year, month + 1, 0).getDate();
    const prevLastDay = new Date(year, month, 0).getDate();

    let elements = [];

    for (let i = firstDOW; i > 0; i--) {
        const date = new Date(year, month - 1, prevLastDay - i + 1);
        elements.push(getDayTemplate(date, "inactive"));
    }

    for (let i = 1; i <= thisLastDay; i++) {
        const date = new Date(year, month, i);
        if (i === new Date().getDate()
            && date.getMonth() === new Date().getMonth()
            && date.getFullYear() === new Date().getFullYear()) {

            elements.push(getDayTemplate(date, "current-day"));
            continue;
        }
        elements.push(getDayTemplate(date));
    }

    for (let i = 1; i < 7 - lastDOW; i++) {
        const date = new Date(year, month + 1, i);
        elements.push(getDayTemplate(date, "inactive"));
    }

    e.dates.innerHTML = "";
    e.dates.append(...elements);
}

function getDayTemplate(date, elemClasses="") {
    const element = document.createElement("li");

    if (elemClasses){
        element.classList.add(elemClasses);
    }

    let htmlBuilder = `<div>${date.getDate()}</div>`;
    const events = [];

    for (let i = 0; i < calEvents.length; i++) {

        const eventDate = new Date(calEvents[i].date);
        eventDate.setMinutes(eventDate.getMinutes() + eventDate.getTimezoneOffset());

        if (eventDate.getDate() === date.getDate()
            && eventDate.getMonth() === date.getMonth()
            && eventDate.getFullYear() === date.getFullYear()) {

            if (events.length < 3) {
                htmlBuilder += `<div class="event" title="${calEvents[i].name}">${calEvents[i].name}</div>`;
            }
            
            events.push(calEvents[i]);
        }
    }

    if (events.length > 3) {
        htmlBuilder += `<div class="event">+${events.length - 3} more</div>`;
    }

    element.addEventListener("click", () => {
        const modal = getModalTemplate(events, date);
        modalContainer.style.display = "flex";
        modalContainer.innerHTML = "";
        modalContainer.append(modal);
    });
    
    element.innerHTML = htmlBuilder;
    return element;
}

function getModalTemplate(events, date) {
    const modal = document.createElement("div");
    modal.classList.add("modal", "flex-col");

    const backButton = document.createElement("button");
    backButton.classList.add("back-button");
    backButton.innerHTML = "×";
    backButton.addEventListener("click", () => {
        modalContainer.style.display = "none";
    });
    modal.append(backButton);

    const label = document.createElement("div");
    label.classList.add("title");
    label.innerHTML = `Events for ${date.toDateString()}:`;
    modal.append(label);

    if (events.length === 0) {
        const noEvents = document.createElement("p");
        noEvents.innerHTML = "No events for this day.";
        modal.append(noEvents);
    } else {
        for (let i = 0; i < events.length; i++) {
            const event = document.createElement("a");
            event.href = "/event/" + events[i].id;
            event.classList.add("event");
            event.innerHTML = `<strong><u>${events[i].name}</u></strong><br>${events[i].description}`
            modal.append(event);
        }
    }

    return modal;
} 

e.prevMonth.addEventListener("click", () => {
    date.setMonth(date.getMonth() - 1);
    updateDates();
});

e.nextMonth.addEventListener("click", () => {
    date.setMonth(date.getMonth() + 1);
    updateDates();
});

updateDates();
console.log(calEvents)