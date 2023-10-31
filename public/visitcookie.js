function getVisits(){

    const cookies = document.cookie
    .split("; ")
    .find((row) => row.startsWith("visits="))
    ?.split("=")[1];

    document.getElementById("visits").innerHTML += cookies

    console.log(cookies)
}