import React, { useState } from "react";
import "./index.css";
import SearchIcon from '@mui/icons-material/Search';
import { Title } from "@material-ui/icons";

function Search( { placeholder, data } ) {

    const [filteredData, setFilteredData] = useState([]);

    const handleFilter = (e) => {
        const searchWord = e.target.value;
        if (searchWord.length > 0) {
            const filter = data.filter((value) => {
                return value.title.toLowerCase().includes(searchWord.toLowerCase());
            });
            setFilteredData(filter);
        }
        if (searchWord.length == 0) {
            setFilteredData([]);
        };
    };

    const handleSelect = (kdrama) => {
        document.getElementById("search-input").value = kdrama.title;
        setFilteredData([]);
    };

    return (
        <div className="search-box">
            <div className="search-bar">
                <input type="text" className="search-input" id="search-input" placeholder="what have you watched recently?" onChange={handleFilter}/>
                <SearchIcon className="search-icon"/>
            </div>
            {filteredData.length != 0 && (
                <div className="results">
                    {filteredData.slice(0, 10).map( (kdrama) => {
                        return (
                            <div onClick={ () => handleSelect(kdrama)}> 
                                {kdrama.title} 
                            </div>
                        )
                    })}
                </div>       
            )}
        </div>
    )
}

export default Search;