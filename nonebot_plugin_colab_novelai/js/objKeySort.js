function objKeySort(obj) {
    let newkey = Object.keys(obj).sort();
    let resStr = '';
    for (let i = 0; i < newkey.length; i++) {
        let str = obj[newkey[i]];
        console.log(i, newkey[i], str);
        resStr += str;
    }
}