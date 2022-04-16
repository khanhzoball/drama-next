import React, { useState, useEffect } from "react";
import banner1 from "./images/banner1.jpg"
import SearchIcon from '@mui/icons-material/Search';

function Home () {
    return (
        <div>
            <div className="hero-container">
                <img src={banner1} className="hero-image"/>
            </div>
            <div className="slogan">
                Welcome to DramaNext!!!
            </div>
            <div className="search-description">
                <span style={{color: "rgb(55, 53, 47)"}}>&#9654;</span> CHOOSE A KDRAMA YOU LIKE AND WE'LL RECOMMEND SOME MORE SIMILAR
            </div>
            <div className="search-box">
                <div className="search-bar">
                    <input type="text" className="search-input" placeholder="what have you watched recently?"/>
                    <div className="search-icon">
                        <SearchIcon />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Home;
  