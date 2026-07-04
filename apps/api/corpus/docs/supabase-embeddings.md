# Generate Embeddings

This guide will walk you through how to generate high quality text embeddings in [Edge Functions](/docs/guides/functions) using its built-in AI inference API, so no external API is required.

## Build the Edge Function

Build an Edge Function that accepts an input string and generates an embedding for it. Edge Functions are server-side TypeScript HTTP endpoints that run on-demand closest to your users.

  

    

      Make sure you have the latest version of the [Supabase CLI installed](/docs/guides/cli/getting-started).

      Initialize Supabase in the root directory of your app and start your local stack.

    

    

      ```shell
      supabase init
      supabase start
      ```

    

  

  

    

      Create an Edge Function that we will use to generate embeddings. We'll call this `embed` (you can name this anything you like).

      This will create a new TypeScript file called `index.ts` under `./supabase/functions/embed`.

    

    

      ```shell
      supabase functions new embed
      ```

    

  

  

    

      Create a new inference session to use for the lifetime of this function. Multiple requests can use the same inference session.

      Currently, only the `gte-small` (https://huggingface.co/Supabase/gte-small) text embedding model is supported in Supabase's Edge Runtime.

    

    
      ```ts ./supabase/functions/embed/index.ts
      const session = new Supabase.ai.Session('gte-small');
      ```
    

  

  

    

      Modify our request handler to accept an `input` string from the POST request JSON body.

      Then generate the embedding by calling `session.run(input)`.

    

    

      ```ts ./supabase/functions/embed/index.ts
      Deno.serve(async (req) => {
        // Extract input string from JSON body
        const { input } = await req.json();

        // Generate the embedding from the user input
        const embedding = await session.run(input, {
          mean_pool: true,
          normalize: true,
        });

        // Return the embedding
        return new Response(
          JSON.stringify({ embedding }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      });
      ```

    

    

      Note the two options we pass to `session.run()`:

      - `mean_pool`: The first option sets `pooling` to `mean`. Pooling refers to how token-level embedding representations are compressed into a single sentence embedding that reflects the meaning of the entire sentence. Average pooling is the most common type of pooling for sentence embeddings.
      - `normalize`: The second option normalizes the embedding vector so that it can be used with distance measures like dot product. A normalized vector means its length (magnitude) is 1 - also referred to as a unit vector. A vector is normalized by dividing each element by the vector's length (magnitude), which maintains its direction but changes its length to 1.

    

  

  

    

      To test the Edge Function, first start a local functions server.

    

    

      ```shell
      supabase functions serve
      ```

    

    

      Then in a new shell, create an HTTP request using cURL and pass in your input in the JSON body.

      ```shell
      curl --request POST 'http://localhost:54321/functions/v1/embed' \
        --header 'Content-Type: application/json' \
        --header 'apikey: SUPABASE_PUBLISHABLE_KEY' \
        --data '{ "input": "hello world" }'
      ```

      Be sure to replace `SUPABASE_PUBLISHABLE_KEY` with your project's publishable key. You can get this key by running `supabase status`.

    

  

## Next steps

- Learn more about [embedding concepts](/docs/guides/ai/concepts)
- [Store your embeddings](/docs/guides/ai/vector-columns) in a database