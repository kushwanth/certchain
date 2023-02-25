<script>
    import { claim_space } from "svelte/internal";

    let query;
    let submit = false;
    let valid = false;
    let queryResult = null;
    function getdata() {
        const url = 'http://127.0.0.1:5002/search';
        const data = fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "query": query })
        }).then((response) => response.json()).then((result) => {
            queryResult = result.hits;
            valid = result.estimatedTotalHits!=0;
        }).catch((error) => {
            console.error('Error:', error);
        });
        submit=true;
    }
  </script>
  
  <div class="p-5 container-fluid text-center">
      <div class="mb-3">
        <label for="query" class="display-3">Enter the query</label><br/><br/>
        <input bind:value={query} class="form-control form-control-lg" id="query" type="text" maxlength="100" required>
      </div><br/>
      <button on:click={getdata} class="btn btn-primary">Submit</button>
  </div>
  
  {#if valid && submit}
  <p class="display-3 text-center">Result</p>
  <div class="table-responsive text-center">
    <table class="table">
        <thead class="table-dark">
          <tr class="row">
            <th class="col">Name</th>
            <th class="col">ID</th>
            <th class="col">Year</th>
            <th class="col">Stream</th>
            <th class="col">Degree</th>
            <th class="col">Institution</th>
          </tr>
        </thead>
        <tbody class="table-hover">
        {#each queryResult as query}
          <tr class="row">
            <td class="col text-break">{query.name}</td>
            <td class="col text-break">{query.registeredNumber}</td>
            <td class="col text-break">{query.issuedDate}</td>
            <td class="col text-break">{query.stream}</td>
            <td class="col text-break">{query.degree}</td>
            <td class="col text-break">{query.institution}</td>
          </tr>
          {/each}
        </tbody>
    </table>
  </div>
  {/if}
  
  {#if !valid && submit}
  <div class="alert alert-danger" role="alert"><p class="display-3 text-center">query is Invalid</p></div>
  {/if}