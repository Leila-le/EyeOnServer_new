function conversionSize(sizeInBytes){
    if( sizeInBytes==='error') {
        sizeInBytes = -1;
        return sizeInBytes.toFixed(2) + 'GB';
    }
    sizeInBytes=parseInt(sizeInBytes);
    const sizeInGB = sizeInBytes / (1024 * 1024 * 1024);
    return sizeInGB.toFixed(2) + 'GB';
}

const sizeTds = document.querySelectorAll('[id$="-size"]');
sizeTds.forEach(td =>{
    const sizeInBytes = td.textContent;
    td.textContent = conversionSize(sizeInBytes);
    console.log(td.textContent);
})
