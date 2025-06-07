const images = [
    {
      src: "${base}/Images/Fuselage.jpg",
      caption: "Fuselage - Main Body of Autogyro",
      link: "https://github.com/Arcilios/Autogyro-CAD-Design/tree/main/Fuselage"
    },
    {
      src: "${base}/Images/PT_Platform.jpg",
      caption: "PT Platform - Sensor Mount Platform",
      link: "https://github.com/Arcilios/Autogyro-CAD-Design/tree/main/Camera"
    }
  ];
  
  const container = document.getElementById("gallery");
  
  images.forEach(img => {
    container.innerHTML += `
      <div class="card">
        <a href="${img.link}" target="_blank">
          <img src="${img.src}" alt="${img.caption}" />
        </a>
        <div class="caption">${img.caption}</div>
      </div>
    `;
  });
  