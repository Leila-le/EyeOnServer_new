function conversionSize(sizeInBytes){
    if( sizeInBytes===-1) {
        return sizeInBytes.toFixed(2) + 'GB';
    }
    sizeInBytes=parseInt(sizeInBytes);
    let sizeInGB = sizeInBytes / (1024 * 1024 * 1024);
    return sizeInGB.toFixed(2) + 'GB';
}

let sizeTds = document.querySelectorAll('[id$="-size"]');
sizeTds.forEach(td =>{
    const sizeInBytes = td.textContent;
    td.textContent = conversionSize(sizeInBytes);
})
