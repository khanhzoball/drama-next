import React, { useState, useEffect } from "react";
import banner1 from "./images/banner1.jpg"

function Home () {
    return (
        <div>
            <div className="hero-container">
                <img src={banner1} className="hero-image"/>
            </div>
            <div>
                <h1>Welcome to DramaNext!!!</h1>
            </div>
        </div>
    )
}

export default Home;
  