// SLP GeoJSON placeholder for choropleth map
// In production, replace with actual GeoJSON of SLP municipalities
const SLP_MUNICIPALITIES = [
    "Ahualulco", "Alaquines", "Aquismon", "Armadillo de los Infante",
    "Axtla de Terrazas", "Cardenas", "Catorce", "Cedral", "Cerritos",
    "Cerro de San Pedro", "Charcas", "Ciudad del Maiz", "Ciudad Fernandez",
    "Ciudad Valles", "Coxcatlan", "Ebano", "El Naranjo", "Guadalcazar",
    "Huehuetlan", "Lagunillas", "Matehuala", "Matlapa",
    "Mexquitic de Carmona", "Moctezuma", "Rayon", "Rioverde", "Salinas",
    "San Antonio", "San Ciro de Acosta", "San Luis Potosi",
    "San Martin Chalchicuautla", "San Nicolas Tolentino",
    "San Vicente Tancuayalab", "Santa Catarina", "Santa Maria del Rio",
    "Santo Domingo", "Soledad de Graciano Sanchez", "Tamasopo",
    "Tamazunchale", "Tampacan", "Tampamolon Corona", "Tamuin",
    "Tancanhuitz", "Tanlajas", "Tanquian de Escobedo", "Tierra Nueva",
    "Vanegas", "Venado", "Villa de Arista", "Villa de Arriaga",
    "Villa de Guadalupe", "Villa de la Paz", "Villa de Ramos",
    "Villa de Reyes", "Villa Hidalgo", "Villa Juarez", "Xilitla",
    "Zaragoza",
];

// Approximate coordinates for main municipalities (for scatter map)
const MUNI_COORDS = {
    "San Luis Potosi": { lat: 22.1498, lon: -100.9792 },
    "Soledad de Graciano Sanchez": { lat: 22.1833, lon: -100.9333 },
    "Ciudad Valles": { lat: 21.9833, lon: -99.0167 },
    "Matehuala": { lat: 23.6500, lon: -100.6500 },
    "Rioverde": { lat: 21.9333, lon: -99.9833 },
    "Tamazunchale": { lat: 21.2667, lon: -98.7833 },
    "Ebano": { lat: 22.2167, lon: -98.5500 },
    "Tamuin": { lat: 22.0000, lon: -98.7500 },
    "Cardenas": { lat: 21.9833, lon: -99.6500 },
    "Cedral": { lat: 23.8167, lon: -100.7167 },
    "Xilitla": { lat: 21.3833, lon: -98.9833 },
    "Aquismon": { lat: 21.6333, lon: -99.0167 },
    "Tamasopo": { lat: 21.9333, lon: -99.3833 },
};
