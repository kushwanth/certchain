<script>
    let hash;
    let submit = false;
    let valid = false;
    let userData = null;
    function getdata() {
        const url = 'http://127.0.0.1:5002/search/'+hash;
        const data = fetch(url, {
            method: 'GET'
        }).then((response) => response.json()).then((result) => {
            userData = Object.entries(result.data);
            valid = true;
        }).catch((error) => {
            console.error('Error:', error);
        });
        submit=true;
    }
  </script>
  
  <div class="p-5 container-fluid text-center">
      <div class="mb-3">
        <label for="hash" class="display-3">Enter the Hash</label><br/><br/>
        <input bind:value={hash} class="form-control form-control-lg" id="hash" type="text" maxlength="128" required>
      </div><br/>
      <button on:click={getdata} class="btn btn-primary">Submit</button>
  </div>
  
  {#if valid && submit}
  <div class="alert alert-success" role="alert"><p class="display-3 text-center">Hash is Valid</p></div><br/>
  <br>
  <div class="container text-center border border-info rounded">
    <p class="display-4 text-center">User Data</p>
    <div class="justify-content-between">
        {#each userData as [key, value]}
        <div class="row">
            <div class="col"><p class="fs-4">{key}</p></div><br>
            <div class="col"><p class="text-break">{value}</p></div><hr>
        </div>
        {/each}
    </div>
  </div>
  {/if}
  
  {#if !valid && submit}
  <div class="alert alert-danger" role="alert"><p class="display-3 text-center">Hash is Invalid</p></div>
  {/if}