function schedule() {
    setTimeout( function () {
        console.log("Hallo nochmal");
        schedule();
    }, 1000);
};

schedule();