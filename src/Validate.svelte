<script>
    let files;
    let submit = false;
    let valid = null;
    let pdfUserData = null;
    let pdfSigData = null
    function upload() {
        const formData = new FormData();
        formData.append('file', files[0]);
        const upload = fetch('http://127.0.0.1:5002/validate', {
            method: 'POST',
            body: formData
        }).then((response) => response.json()).then((result) => {
            valid = result.valid;
            pdfUserData = Object.entries(result.data);
            delete result.valid;
            delete result.data;
            let sigIsuuer = result.issuer;
            delete result.issuer;
            pdfSigData = Object.entries({...sigIsuuer,...result});
  
        }).catch((error) => {
            console.error('Error:', error);
        });
        submit=true;
        console.log(pdfSigData,pdfUserData);
    }
  </script>
  
  <div class="p-5 container-fluid text-center">
      <div class="mb-3">
        <label for="file" class="display-3">Upload the Signed Certificate</label><br/><br/>
        <input bind:files class="form-control form-control-lg" id="file" type="file" accept="application/pdf" required>
      </div><br/>
      <button on:click={upload} class="btn btn-primary">Submit</button>
  </div>
  
  {#if valid && submit}
  <div class="alert alert-success" role="alert"><p class="display-3 text-center">Certificate is Valid</p></div><br/>
  <br>
  <div class="container text-center border border-info rounded">
    <p class="display-4 text-center">Signature Data</p>
    <div class="justify-content-between">
        {#each pdfSigData as [key, value]}
        <div class="row">
            <div class="col"><p class="fs-4">{key}</p></div><br>
            <div class="col"><p class="text-break">{value}</p></div><hr>
        </div>
        {/each}
    </div>
    <br/>
    <p class="display-4 text-center">User Data</p>
    <div class="justify-content-between">
      {#each pdfUserData as [key, value]}
      <div class="row">
        <div class="col"><p class="fs-4">{key}</p></div><br>
        <div class="col"><p class="text-break">{value}</p></div><hr>
      </div>
      {/each}
    </div>
  </div>
  {/if}
  
  {#if !valid && submit}
  <div class="alert alert-danger" role="alert"><p class="display-3 text-center">Certificate is Invalid</p></div>
  {/if}