function getLimitesTrimestre(year, month) {
    if (month < 0) {
        year -= 1;
        month += 12;
    }
    let q1 = {
        mi: 0,
        mf: 2,
        df: 31
    }
    let q2 = {
        mi: 3,
        mf: 5,
        df: 30
    }
    let q3 = {
        mi: 6,
        mf: 8,
        df: 30
    }
    let q4 = {
        mi: 9,
        mf: 11,
        df: 31
    }

    let mapper = {
        0: q1,
        1: q1,
        2: q1,
        3: q2,
        4: q2,
        5: q2,
        6: q3,
        7: q3,
        8: q3,
        9: q4,
        10: q4,
        11: q4,
    }

    let q = mapper[month];
    return {
        li: new Date(year, q.mi, 1),
        ls: new Date(year, q.mf, q.df, 23, 59, 59, 999)
    }
}

function limitesMesActual() {
    let now = new Date();
    return {
        li: new Date(now.getFullYear(), now.getMonth(), 1),
        ls: new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999)
    }
}

function limitesMesAnterior() {
    let now = new Date();
    return {
        li: new Date(now.getFullYear(), now.getMonth() - 1, 1),
        ls: new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59, 999)
    }
}

function limitesTrimestreActual() {
    let now = new Date();
    return getLimitesTrimestre(now.getFullYear(), now.getMonth());
}

function limitesTrimestreAnterior() {
    let now = new Date();
    return getLimitesTrimestre(now.getFullYear(), now.getMonth() - 3);
}

function limitesAnioActual() {
    let now = new Date();
    return {
        li: new Date(now.getFullYear(), 0, 1),
        ls: new Date(now.getFullYear(), 11, 31, 23, 59, 59, 999)
    }
}

function limitesAnioAnterior() {
    let now = new Date();
    return {
        li: new Date(now.getFullYear() - 1, 0, 1),
        ls: new Date(now.getFullYear() - 1, 11, 31, 23, 59, 59, 999)
    }
}

export function getLimitesPeriodo(periodo) {
    let mapper = {
        mes_actual: limitesMesActual,
        mes_anterior: limitesMesAnterior,
        trimestre_actual: limitesTrimestreActual,
        trimestre_anterior: limitesTrimestreAnterior,
        anio_actual: limitesAnioActual,
        anio_anterior: limitesAnioAnterior,
    };
    return mapper.hasOwnProperty(periodo) ? mapper[periodo]() : null;
}