import React, { useState, useEffect } from "react";
import banner1 from "./images/banner1.jpg"
import SearchIcon from '@mui/icons-material/Search';
import Search from "./search";
import kdrama from "./kdrama.json"

function Home () {
    return (
        <div>
            <div className="hero-container">
                <img src={banner1} className="hero-image"/>
            </div>
            <div className="slogan">
                Welcome to DramaNext!
            </div>
            <div className="search-description">
                <span style={{color: "rgb(55, 53, 47)"}}>&#9654;</span>&nbsp; CHOOSE A KDRAMA YOU LIKE AND WE'LL RECOMMEND SOME MORE SIMILAR
            </div>
            <Search data={kdrama}/>
        </div>
    )
}

export default Home;
  