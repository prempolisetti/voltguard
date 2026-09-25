import { initializeApp }
    from "https://www.gstatic.com/firebasejs/12.19.0/firebase-app.js";

import {
    getDatabase,
    ref,
    onValue
} from "https://www.gstatic.com/firebasejs/12.19.0/firebase-database.js";


const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "volt-gaurd.firebaseapp.com",
    databaseURL: "https://volt-gaurd-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "volt-gaurd",
    storageBucket: "volt-gaurd.firebasestorage.app",
    messagingSenderId: "282062494637",
    appId: "1:282062494637:web:218d171ac55c9c89341f24",
    measurementId: "G-9H4KCRYLJX"
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);


// Connect to Realtime Database
const database = getDatabase(app);


// Get device01
const deviceRef = ref(database, "device01");


// Listen for Firebase changes
onValue(deviceRef, (snapshot) => {

    const data = snapshot.val();

    console.log("Firebase data:", data);

    if (data) {

        document.getElementById("voltage").textContent =
            data.voltage + " V";

        document.getElementById("current").textContent =
            data.current + " A";

        document.getElementById("temperature").textContent =
            data.temperature + " °C";

        document.getElementById("status").textContent =
            data.Status;

    }

});